# SimDroid
Computing static similarity between android packages

__Version: `2.0`__

### Made with 

SimDroid is made using [![androguard_v1.5](https://storage.googleapis.com/google-code-archive/v2/code.google.com/androguard/logo.png)](https://github.com/androguard/androguard/)

## Documentation

* Clone the repo

* Move to repo dir
```
$ cd Simdroid
```

* Create Analysis folder
```
$ mkdir Analysis_androgd
```
  * Create analysis result dir
  ```
  $ mkdir Analysis_androgd/exodus
  ``` 

* Move to __`simdroid`__ folder
```
$ cd simdroid
```

* Run __`androsim`__
```
$ python androsim.py -i [android_apk1] [android_apk2]
```

#### Result 
* Check in `../Analysis_androgd/exodus`

### License

[License](LICENSE)

