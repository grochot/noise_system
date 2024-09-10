# NoiseMeasurement App 

## Connections: 

### 1. Lockin Time: 

![image](docs/scheme_lockin_time_mode.drawio.png)


### 2. Lockin field: 
![image](docs/scheme_lockin_field_mode.drawio.png)


### 3. Lockin frequency: 

![image](docs/scheme_lockin_frequency_mode.drawio.png)


## Hdc Mode 

In order to use the option of setting a field vector with the variable “Hr”, it is necessary to enter a vector in the “Vector” field, the last element of which will be the variable “Hr” as in the example below. 

```python 
0,1,10,4,20,5,Hr
```
Then, from the sequencer, select the change by the parameter “Hr” and enter the range of its variation: 
![image](docs/sequencer.png)