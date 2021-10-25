## is3-python-broker 

![](/figures/broker_architecture.jpg)

## Reinforcement Learning

***Warning: The Python broker has not yet been extensively tested. There are still many problems.***

The IS3 Python broker only creates consumption tariffs. All other tariffs are created in the same manner as the previous version of the broker. 

The RL agent is a simple MLP that takes as input an observation of 81 scalar numbers and outputs an action of 5 scalar numbers, and is trained using A2C (Advantage Actor-Critic). The observation space and action space of the environment are defined in `powertac_env.py`.  

The 81-vector **observation** is made of: 
- 24 grid imbalance predictions outputted by the Seq2Seq predictor (one per hour for the next 24 hours)
- 24 customer prosumption predicitons outputted by the Seq2Seq predictor (one per hour for the next 24 hours)
- 24 one-hot values encoding the time-of-day 
- 7 one-hot values encoding the day-of-week
- the current timeslot in the game 
- the market's current percentual deviation (defined the same as in EWIIS3 2020)  

Definition of the observed percentual deviation: Let `MUBP` be the mean-usage based price for a given consumption tariff, and `MUBP_min` the smallest such `MUBP` across all active consumption tariff (not including the broker's own consumption tariff), and let `MUBP_IS3` be the IS3 broker's own consumption tariff, then the percentual deviation is defined as 

```
percentual_deviation = (MUBP_min - MUBP_IS3)/|MUBP_min|
```

The 5-vector **action** is made of:  
- mean percentual deviation
- std percentual deviation
- mean periodic payment factor
- std periodic payment factor
- the probability of starting a new iteration

The broker uses the same time-of-use tariff scheme as the previous version (see `StdConsumptionTariff` in the Java broker), which is constructed using a MUBP and PPF. The MUBP can be calculated from the mean percentual deviation. During training, both the MUBP and PPF can be sampled from the normal distribution with the above mean and std, which can also aid in exploration, while during inference, one can simply use the mean. The broker also predicts whether to start a new 'iteration' (same definition as before) in the next timeslot. 

The **reward** is simply the sum of past charges. There's not any kind of penalty. 


## Seq2Seq

Rough sketches of the Seq2Seq architectures for the grid imbalance and customer prosumption prediction models. Each model takes in the 128 past and present timeslots and predicts the future 24 timeslots. In order to make this prediction, it also takes into account temperature, cloud cover, wind speed, day-of-week and hour-of-day features. For the future timeslots, real weather data is substituted by weather forecasts.

### 1. Basic Seq2Seq

The basic Seq2Seq model consists of two recurrent networks: the encoder network and decoder network. The encoder network processes the input sequence one timestep at a time. At each point in time, the network produces an output and a memory state. The memory state is passed on to the same network at the next timestep. At the end of the encoder's input sequence, the encoder network passes a 'thought vector' as a representation of the entire sequence to the decoder. The decoder, from that thought vector and the decoder input sequence, produces the output sequence one timestep at a time. 

Other than shown in this drawing, the implemented Seq2Seq does not currently pass the output from one decoder timestep as input to the next decoder timestep. 

![](/figures/Seq2Seq%20basic%20powertac.jpg)

### 2. Seq2Seq with context vector

Instead of relying on the decoder network to remember all the information about the encoder sequence via the memory state, the final encoder network's output (acting as an additional representation of the encoder sequence) is passed in a time-distributed fashion as an input feature to each decoder timestep. This vector is then referred to as the context vector since it provides the decoder with context to help predict the next decoder step. 

![](/figures/Seq2Seq%20context-vector%20powertac.jpg)

### 3. Bidirectional Seq2Seq with context vector and attention mechanism

Additionally, the Seq2Seq model can be extended by an attention mechanism to allow for information to flow more easily from individual encoder timeslots that are particularly relevant for any given decoder timeslot. In order to achieve this, for each decoder timeslot, a query vector is computed that contains information about what is needed to predict the current decoder timeslot. Also, for each encoder timeslot a key vector and value vector is computed once. The key vector is computed such that it can be compared easily to the query vector while the value vector contains the actually relevant information to be passed to the decoder. After the query vector has been computed for a given decoder timeslot, its similarity to each key vector is computed. These similarity scores are then fed into the softmax function to get a probability distribution (aka attention distribution) over encoder timeslots. All the encoder value vectors are then weighted by their respective softmax-normalized similarity score (aka attention weight) and summed up to get a single attention-weighted value vector. This vector contains all the information that is deemed relevant by the attention mechanism for this particular decoder timeslot. 

Especially in the context of an attention mechanism, a bidirectional encoder network can make sense such that the keys and values can take all of the timeslot's surroundings into account to produce an accurate picture of what is happening at this point in time. A bidirectional encoder simply processes the input sequence using two separate recurrent sub-networks, one from left to right (original order) and one from right to left (reverse order). The outputs of these two sub-networks at each timeslot are concatenated and passed on to the next layer. Furthermore, the final memory states are concatenated and passed on to the decoder as a single encoder sequence representation.

![](/figures/Seq2Seq%20attention%20bidirectional%20powertac.jpg)

## Future 

Ideas for future improvements: 
- use more market information as input features 
- make it easy to add new tariffs to the RL broker, e.g. when you add a new tariff in the Java broker, this should correspond to a learned tariff in the Python broker; at the moment, this is only the case for the consumption tariff 
- transformer neural networks instead of Seq2Seq predictor 
- transformer neural network to turn predictions (and possibly additional features) into bids 
- MCTS for bidding 
- use LSTM for the broker
- train on many more games
- test the broker's behaviors: what do the tariffs look like that it creates? based on what MUBP and PPF does it create tariffs? when does it start a new iteration? what is the value for different states (difficult to visualize since the observation space has 81 dimensions, but at least for a subset of observation features, while averaging over the other features, most importantly the percentual deviation)?

Possible future Python broker architecture:  

![](/figures/broker_architecture.jpg)
