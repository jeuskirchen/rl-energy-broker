import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from data.customer import load_prosumption_weather_time
from data.grid import load_grid_imbalance


os.environ["CUDA_VISIBLE_DEVICES"] = ""


class Seq2SeqPredictor:

    def __init__(self, target: str, time_horizon: int = 128) -> None:
        assert target in ("grid_imbalance", "customer_prosumption"), "Error: There is no Seq2Seq model for this target."
        self.target = target  # what is being predicted? either "grid_imbalance" or "customer_prosumption"
        self.time_horizon = time_horizon  # how many past timeslots to take into account to make a prediction?
        filename = "seq2seq_customer_prosumption_06_and_07_2021.h5" if target == "customer_prosumption" else "seq2seq_grid_imbalance_06_and_07_2021.h5"
        assert os.path.exists(
            f"predictor/models/{filename}"), f"Error: h5 file with {self.target} model parameters is missing."
        self.model = load_model(f"predictor/models/{filename}")
        # De-normalization/de-standardization statistics
        # (see Dataset_GridImbalance.ipynb, Dataset_CustomerProsumption.ipynb)
        self.mean = -8227.517005199943 if target == "customer_prosumption" else -6718.869614781172
        self.std = 13210.734393502056 if target == "customer_prosumption" else 18940.379106236847

    def get_prediction(self, game_id: str, timeslot: int) -> pd.DataFrame:
        """
        In order for the neural network to process the data, it needs to be turned into a set of examples. In this case,
        we keep 6 separate sets depending on the type of feature and whether it's fed to the encoder or decoder. The
        i-th entry in each set is 1 example and is a sequence of vectors. The sequence length is 128 for encoder features
        and 24 for decoder features. The length of each vector depends on the feature: for day-of-week it's 7 (since it's
        a one-hot vector of weekdays), for hour-of-day it's 24 (one-hot over hours), for weather it's 3 (temperature,
        cloud cover and wind speed) and for features it's either 3 or 4 depending on whether it's fed to the encoder or
        decoder: the decoder features only contain weather data, so it's 3, the encoder features also contain the past
        grid imbalance or customer prosumption, so it's 4.
        """

        # Load data for this timeslot:
        if self.target == "grid_imbalance":
            encoder_dataframe, decoder_dataframe = load_grid_imbalance(game_id, timeslot)
        elif self.target == "customer_prosumption":
            encoder_dataframe, decoder_dataframe = load_prosumption_weather_time(game_id, timeslot)
        else:
            encoder_dataframe, decoder_dataframe = None, None
        # Encoder data (dow, hod, weather, past target values) for 128 past timeslots (up to and including the current timeslot)
        # Decoder data (dow, hod, weather_forecasts) for 24 future timeslots

        # Encoder features:
        x_enc_dow = encoder_dataframe["dayOfWeek"]  # day-of-week
        x_enc_dow = np.array([[float(row == day) for day in range(1, 8)] for row in x_enc_dow])  # to one-hot vector
        x_enc_dow = x_enc_dow.reshape(1, -1, 7)  # turn into batch of size 1 (should be size (1, 128, 7), for time horizon of 128)
        x_enc_hour = encoder_dataframe["slotInDay"]  # hour-of-day
        x_enc_hour = np.array([[float(row == hour) for hour in range(1, 25)] for row in x_enc_hour])  # to one-hot vector
        x_enc_hour = x_enc_hour.reshape(1, -1, 24)  # turn into batch of size 1 (should be size (1, 128, 24))
        x_enc_features = np.array([
            encoder_dataframe["temperature"],
            encoder_dataframe["cloudCover"],
            encoder_dataframe["windSpeed"],
            encoder_dataframe["netImbalance" if self.target == "grid_imbalance" else "SUM_kWH"]
        ])
        x_enc_features = x_enc_features.reshape(1, -1, 4)  # turn into batch of size 1 (should be size (1, 128, 4))

        # Decoder features:
        # 24 next weather forecasts are all available and stored for the present timeslot !!!
        x_dec_dow = decoder_dataframe["dayOfWeek"]  # day-of-week
        x_dec_dow = np.array([[float(row == day) for day in range(1, 8)] for row in x_dec_dow]) # to one-hot vector
        x_dec_dow = x_dec_dow.reshape(1, -1, 7)  # turn into batch of size 1 (should be size (1, 24, 7))
        x_dec_hour = decoder_dataframe["slotInDay"]  # hour-of-day
        x_dec_hour = np.array([[float(row == hour) for hour in range(1, 25)] for row in x_dec_hour]) # to one-hot vector
        x_dec_hour = x_dec_hour.reshape(1, -1, 24)  # turn into batch of size 1 (should be size (1, 24, 24))
        x_dec_features = np.array([
            decoder_dataframe["temperature"],
            decoder_dataframe["cloudCover"],
            decoder_dataframe["windSpeed"]
        ])
        x_dec_features = x_dec_features.reshape(1, -1, 3)  # turn into batch of size 1 (should be size (1, 24, 3))

        # Make prediction:
        y_pred = self.model.predict((
            x_enc_dow,  # day-of-week
            x_enc_hour,  # hour-of-day
            x_enc_features,  # weather + grid imbalance OR customer prosumption, depending on the model
            x_dec_dow,  # day-of-week
            x_dec_hour,  # hour-of-day
            x_dec_features))  # weather forecasts instead of actual weather data (no grid imbalance or customer prosumption)
        # The second output is an attention tensor that I only used for visualization purposes during development.
        # y_pred has shape (1, 24, 1)
        y_pred = y_pred.reshape(-1)  # now it has shape (24,)

        # De-normalize/de-standardize:
        y_pred = y_pred * self.std + self.mean

        df_prediction = pd.DataFrame({
            "target_timeslot": decoder_dataframe["targetTimeslotIndex"],
            "prediction": y_pred,
            "prediction_timeslot": decoder_dataframe["postedTimeslotIndex"],
            "proximity": decoder_dataframe["proximity"],
        })
        df_prediction["game_id"] = game_id
        df_prediction["target"] = self.target[:self.target.find("_")]  # {"grid", "customer"}
        df_prediction["type"] = self.target[self.target.find("_")+1:]  # {"imbalance", "prosumption"}

        return df_prediction
