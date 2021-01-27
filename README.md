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

#### Analysis Result 
* Check in `../Analysis_androgd/exodus`

### bibtex
```
@InProceedings{10.1007/978-3-030-05171-6_8,
author="Kishore, Sreesh and Kumar, Renuka and Rajan, Sreeranga",
title="Towards Accuracy in Similarity Analysis of Android Applications",
booktitle="Information Systems Security",
year="2018",
publisher="Springer International Publishing",
address="Cham",
pages="146--167",
isbn="978-3-030-05171-6"
}

```

### License

[License](LICENSE)

