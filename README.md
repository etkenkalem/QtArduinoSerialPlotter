# QtArduinoSerialPlotter
Arduino Serial Plotter, pyqtgraph
![plotterInfo](/screenShots/heater3.png)
### Requirements
- Python 3.8+

### Install
```sh
pip install PyQt5 pyqtgraph qdarkstyle qtawesome
```
### Run
```sh
python qtArduinoSerialPlotter.py
```

![plotterInfo](/screenShots/plottertx.gif)

### Basic usage

- Only data
  ```cpp
    String data ="pltr#["+String(x)+","+String(y)+"]";
  ```
- Add label
  ```cpp
    String data ="pltr#["+String(x)+","+String(y)+",lbl1]";
  ```
- Add Color (#f00)
  ```cpp
    String data ="pltr#["+String(x)+","+String(y)+",lbl1,f00]";
  ```
- Arduino Example

```cpp

void setup() {
  Serial.begin(115200); 
}

float x=0.0;
char buffer[200];

void loop() {  
  float y=x*x*x;
  y=y/100.0;

  //"pltr#[xValue,yValue,Label]"
  String data="pltr#["+String(x)+","+String(y)+",Lbl1]";
  Serial.println(data);  
  x++;
  
  delay(200);  
  
  while (Serial.available() > 0) {   
    if (Serial.read() == '\n') {      
      Serial.println("ok");    
    }
  }
}
```

![image](/screenShots/heater.png)



- One graph scene multi line
  ```cpp
    String data ="pltr#["+String(x)+","+String(y)+",lbl1:"+String(x)+","+String(y+5)+",lbl2]";
  ```
- Multi graph scene multi line
  ```cpp
    String data ="pltr#["+String(x)+","+String(y)+",lbl1:"+String(x)+","+String(y+5)+",lbl2]#["+String(x)+","+String(y+20)+",lbl3]";
  ```

