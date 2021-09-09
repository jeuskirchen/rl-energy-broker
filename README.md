## ewiis3-python-broker 

![](/figures/broker_architecture.jpg)


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
