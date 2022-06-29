# nvdla-compiler-learning#
# 1.安装准备与一些有用的资源 #
## 1.1.github地址 ##
	https://github.com/nvdla
## 1.2.编译和安装 ##
### 1.2.1.参考信息 ###
	https://blog.csdn.net/zhajio/article/details/84784336 
	https://blog.csdn.net/hywCogost/article/details/82114529
### 1.2.2.问题与解决 ###

- ubuntu16.04编译会出现：“  undefined reference to google::protobuf::internal::empty_string_[abi:cxx11]   ”等链接错误，原因是ubuntu16.04默认安装的是GCC5，但是nvdla的sw部分应该是用的GCC5以下的版本，google上有人讲到：“  the ABI for std::string has changed in GCC 5(related to c++ 11 requirements, but it applies even if you aren't using c++ 11   ”，解决方法是：可以在g++的编译参数中加入 -D_GLIBCXX_USR_CXX11_ABI=0, 然后就解决了，具体修改文件是nvdla/sw/umd/core/src/compiler/Makefile 把上述的字符串加到MODULE_CPPFLAGS.....以后最末尾即可编译通过

- **tools/bin/tmake -build cmod_top - can't build cmod_top**

  一般在Ubuntu14.04（gcc, g++ 4.8.4), 16.04 (gcc, g++ 5.4.0)可以顺利编译通过，在18.04 (gcc, g++ 8.x)以上会编译报错。因为hw支持的是低版本gcc, g++，如果要加入对高版本gcc，g++的支持，可以在**cmod/hls/include 目录下更新Algorithmic C**。

  详细见 [Fix CMOD Makefile calling system GCC linker instead of user GCC #191](https://github.com/nvdla/hw/pull/191)

  ```shell
  # 笔者解决方案
  cd PATH_TO_CMOD_HLS_INCLUDE
  git clone https://github.com/hlslibs/ac_types tmp
  cp tmp/include/* ./
  rm -rf tmp
  ```
- **$ cmake部分出现-Could NOT find Lua**

  ``` -- Searching for SystemC
  -- SystemC version = 2.3.0
  -- SystemC library = /usr/local/systemc-2.3.0/lib-linux64/libsystemc.so
  -- Searching for TLM
  running ls /usr/local/systemc-2.3.0/include/tlm.h 2>&1
  /usr/local/systemc-2.3.0/include/tlm.h
  -- TLM library = /usr/local/systemc-2.3.0/include/tlm.h
  CMake Error at /usr/share/cmake-3.10/Modules/FindPackageHandleStandardArgs.cmake:137 (message):
  Could NOT find Lua (missing: LUA_LIBRARIES LUA_INCLUDE_DIR)
  Call Stack (most recent call first):
  /usr/share/cmake-3.10/Modules/FindPackageHandleStandardArgs.cmake:378 (_FPHSA_FAILURE_MESSAGE)
  cmake/FindLua.cmake:113 (FIND_PACKAGE_HANDLE_STANDARD_ARGS)
  CMakeLists.txt:55 (find_package)
  ```
  原因是缺少Lua5.2相关脚本环境。$ sudo apt-get install liblua5.2即可。
### 1.2.3使用docker直接使用完备的环境

  ​使用docker可以一步到位，避免搭建环境时各种不必要的错误。

  1. 安装docker

  2. 从docker运行nvdla虚拟模拟器

	$ docker pull nvdla/vp
	*从dockerhub里下载nvdla/vp镜像*

	$ docker run -it -v /data1/wangyizhi/home:/home --name wyz_docker nvdla/vp 
	*运行一个docker，同时建立主机下/data1/wangyizhi/home文件夹到docker下/home的文件夹映射（双向映射），同时取名docker为wyz_docker*

	$ cd /usr/local/nvdla

	$ aarch64_toplevel -c aarch64_nvdla.lua
	*运行lua脚本*

	Welcome to Buildroot
	nvdla login: root
	Password: nvdla
	*进入到nvdla虚拟模拟环境#命令行*

	# mount -t 9p -o trans=virtio r /mnt
	*mount挂载一下*

	# cd /mnt

	# ls

	Image            libnvdla_compiler.so
	LICENSE           libnvdla_runtime.so
	aarch64_nvdla.lua      **nvdla_compiler**
	aarch64_nvdla_dump_dts.lua **nvdla_runtime**
	drm.ko           opendla_1.ko
	efi-virtio.rom       opendla_2.ko
	init_dla.sh         rootfs.ext4

	至此可以在此环境下对caffe网络进行编译和运行。
	```

  3. 导入caffemodel和 prototxt  文件进行编译和仿真
	
	```
	# ./nvdla_compiler [-options] --prototxt <prototxt_file> --caffemodel <caffemodel_file> -o <outputpath>
	# ./nvdla_runtime --loadable <loadable_file> --image <image_file>
	```
  4. 有个问题
  
	在docker的nvdla的vp下：
	# ./nvdla_compiler -h
	./nvdla_compiler: line 2: syntax error: unexpected redirection
	# ./nvdla_compiler: line 1:ELF: not found
	# ./nvdla_runtime -h
	Usage: ./nvdla_runtime [-options] --loadable <loadable_file>
	where options include:
	    -h                    print this help message
	    -s                    launch test in server mode
	    --image <file>        input jpg/pgm file
	    --normalize <value>   normalize value for input image
	    --mean <value>        comma separated mean value for input image
	    --rawdump             dump raw dimg data

	在docker下：
	root@b8db90f265c9:/usr/local/nvdla# ./nvdla_compiler -h
	Usage: ./nvdla_compiler [-options] --prototxt <prototxt_file> --caffemodel <caffemodel_file>
	where options include:
	    -h                                                 print this help message
	    -o <outputpath>                                    outputs wisdom files in 'outputpath' directory
	    --profile <basic|default|performance|fast-math>    computation profile(fast-math by default)
	    --cprecision <fp16|int8>                           compute precision(fp16 by default)
	    --configtarget <nv_full|nv_large|nv_small>         target platform(opendla-full by default)
	    --calibtable <int8 calib file>                     calibration table for INT8 networks
	    --quantizationMode <per-kernel|per-filter>         quantization mode for INT8(per-kernel by default)

	root@b8db90f265c9:/usr/local/nvdla# ./nvdla_runtime -h
	bash: ./nvdla_runtime: cannot execute binary file: Exec format error
	
	可以发现nvdla_compiler和nvdla_runtime在两个环境下各有一个没法运行，使用fie查看其依赖环境。
	file查看
	
	root@ac3852e4d38a:/usr/local/nvdla# file nvdla_compiler
	nvdla_compiler: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), dynamically linked, 
	interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.24, BuildID[sha1]=3e353cdcba7281d79d2dcc8c605a106b54fdf01f, 
	not stripped

	root@ac3852e4d38a:/usr/local/nvdla# file nvdla_runtime
	nvdla_runtime: ELF 64-bit LSB executable, ARM aarch64, version 1 (GNU/Linux), dynamically linked, 
	interpreter /lib/ld-linux-aarch64.so.1, for GNU/Linux 3.7.0, BuildID[sha1]=ee8c403968b2e61360ea8b2eef3c2c625fbff496, 
	not stripped
	
	
	结论：vp模拟目标板所以是arm64，于是基于arm64的runtime能运行；主机能运行基于x86的compiler。
	compiler跑在pc上，交叉编译好之后runtime跑在目标板上即可。

	查看nvdla/vp的docker tag, 1.4是最新的，vp里面已经没有compile了只有runtime.20191118
	
## 1.3.软硬件分析文章参考 ##

	https://github.com/JunningWu/Learning-NVDLA-Notes
# 2.源代码结构 #

## 2.1.整体代码目录结构 ##
## 2.2.hw目录结构 ##
![](https://github.com/zeasa/nvdla-compiler/raw/master/document/imgs/hwfolderlist.png)

- cmod是systemc模型用来仿真和vp
- perf是性能计算excel表格
- spec是配置和工程文件
- sync是综合配置
- tool是build和pl脚本等工具
- verif是仿真文件夹
- vmod是verilog仿真模型和RTL代码
## 2.3.sw目录结构 ##
![](https://github.com/zeasa/nvdla-compiler/raw/master/document/imgs/swfolderlist.png)

- umd是runtime的上层部分，运行在用户态，负责解析loadable文件并提交给kmd驱动硬件执行计算任务
- kmd接受umd的工作负载提交，并驱动硬件DLA执行计算任务
- prebuild

# 3.模型编译与DLA仿真运行 #
# 4.深入源码 #
## 4.1.总体结构与代码的日志系统 ##

### 4.1.1.代码总体结构

​	nvdla的软件代码部分主要分为umd和kmd，这两部分的作用在前面sw目录结构部分已经说过。其中umd包括了runtime的userspace部分和compiler部分。umd文件夹包括了如下几个文件夹，下面说明其功能：

- apps：包括了runtime的入口以及compiler的入口
- core：runtime和compiler的主要实现逻辑放在这里，也是需要着重阅读的部分
- externel：这个目录存放了umd用到的第三方库，需要说明的是protobuf主要用于caffe模型的解析，因为caffe的blob格式原始存储方式是使用了google开发的protobuf
- make：umd的编译makefile
- port：主要是runtime的底层访问API，为了实现OS无关，做了这个隔离层，目前只实现了Linux下的。这层API包括内存访问，用户态和内核态的交互IOCTL，内存分配等。需要注意的是NVDLA的runtime部分用户态和内核态交互使用了Linux用于显卡抽线的DRM接口
- utils：这个文件夹放了几个通用的模块，包括BitBinaryTree以及伙伴内存管理等。其中伙伴内存管理模块在compiler的tensor内存分配推导部分有用到

### 4.1.2.日志系统

​	nvdla的sw部分，文档比较缺乏，在nvdia的官方网站只有半页简单介绍，关于软件框架，层次结构一概为止。代码里面注释也很少，只有在涉及部分算法的函数有很少的几行简单的说明。好在nvdla的sw软件代码里，有较为详细的log日志生成功能，可以将代码在编译的过程中的内部数据结构和变量很好的展示出来，在代码阅读过程中有很大的帮助，很多读不懂的部分，看看日志就能明白其中的联系。

​	nvdla的日志，在代码里默认都是关闭的，并且没有总体的开关，log开关都是分散在各个类的定义文件里。下面举个例子：

![](https://github.com/zeasa/nvdla-compiler/raw/master/document/imgs/logswitch.png)

上图中在Graph这个类里面，有许多的log日志开关，只需将红框中的false改为true就可以打开这个class的日志输出。类似的开关还有很多，需要在读到相关class部分代码的时候有需要的打开。以编译一个Lenet5的网络为例，输出的日志在10000行左右，这个log.txt在本repo的model&log文件夹里可以找到。

## 4.2.runtime部分 ##

### 4.2.1.总体概述

​	​	 runtime主要是接收nvdla 编译出来的loadable文件，并且对loadable文件进行反解码操作。在NVDLA和Tengine对接的过程中，将Loadable序列化和反序列化的过程省略，直接将编译的信息导入到runtime对象中进行编译信息的解析。在解析完成后，根据编译的信息对神经网络的张量分配内存，接着将编译信息通过IOTCL向下传递到内核态。

### 4.2.2.结构和执行流程分析

​	ToDo

## 4.3.compiler部分 ##

### 4.3.1.总体概述

​	compiler部分的代码主要在sw/umd/core/src/compiler目录里，经过阅读，发现nvdla现有的compiler代码前端只支持caffe一种前端框架，在调用compiler进行模型编译的时候，命令行参数需要指定caffe模型的prototxt文件以及train好的model的部署文件(包括了weight和bias等参数)。caffe模型的prototxt文件格式具体可以参考caffe框架相关文档。以下是一个prototxt文件的一部分：

```js
name: "LeNet"
layer {
  name: "data"
  type: "Input"
  top: "data"
  input_param { shape: { dim: 64 dim: 1 dim: 28 dim: 28 } }
}
layer {
  name: "conv1"
  type: "Convolution"
  bottom: "data"
  top: "conv1"
  param {
    lr_mult: 1
  }
  param {
    lr_mult: 2
  }
  convolution_param {
    num_output: 20
    kernel_size: 5
    stride: 1
    weight_filler {
      type: "xavier"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  name: "pool1"
  type: "Pooling"
  bottom: "conv1"
  top: "pool1"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
```

从这个例子可以看出，同大多框架的网络模型定义相似，网络定义都是以layer为主，顺序定义，语法为JSON。每层包括了name，type和param等参数，其中layer的type以及每种type的layer的参数在caffe框架的定义文件里有详细的描述。上面这个例子只截取了一个LeNet5网络的前3层，分别是Input、conv1、pooling等。

​	caffemodel文件是训练后带有网络权重信息的模型文件，使用的是google的protobuf格式二进制存储，使用caffemodel2json工具可以将其解析为json格式以便查看，下面是对应上述prototxt文件lenet5网络的json结果的一部分：

```js
dump
{
  "name": "LeNet",
  "layer": [ 
    { #这一层是LeNet的输入层
      "name": "mnist",
      "type": "Data",
      "top": [
        "data",
        "label"
      ],
      "include": [
        {
          "phase": 0 #表明当前层只有TRAIN阶段才包含进来
        }
      ],
      "phase": 0, #训练或者测试阶段 TRAIN=0, TEST=1
      "transform_param": {
        "scale": 0.00390625
      },
      "data_param": {
        "source": "examples/mnist/mnist_train_lmdb",
        "batch_size": 64,
        "backend": 1
      }
    },
    { #这一层是LeNet紧接着输入层的第一个conv层
      "name": "conv1",
      "type": "Convolution",
      "bottom": [
        "data"
      ],
      "top": [
        "conv1"
      ],
      "param": [
        {
          "lr_mult": 1.0 #weight的学习率
        },
        {
          "lr_mult": 2.0 #bias的学习率
        }
      ],
      "blobs": [ #这里的blobs存储的是这一层的卷积kernel的weight和bias信息
        { #blobs[0]应该是weight权重，从shape看出有20个kernel，每个5*5*1
          "data": [
            0.17512507736682892,
            0.20436875522136688,
            0.056398797780275345,
            0.005825345404446125,
            0.23611973226070404,
            "(495 elements more)"
          ],
          "shape": {
            "dim": [
              20, #N
              1,  #C
              5,  #H
              5   #W
            ]
          }
        },
        { #blobs[1]应该是bias值，shape是20
          "data": [
            -0.05203453078866005,
            -0.26182013750076294,
            -0.1220993623137474,
            -0.07315845042467117,
            0.002272228477522731,
            "(15 elements more)"
          ],
          "shape": {
            "dim": [
              20
            ]
          }
        }
      ],
      "phase": 0,
      "convolution_param": {
        "num_output": 20,
        "kernel_size": [
          5
        ],
        "stride": [
          1
        ],
        "weight_filler": {
          "type": "xavier"  #权值初始化方法
        },
        "bias_filler": {
          "type": "constant" #权值初始化方法
        }
      }
    },
```

​	接下来compiler会对prototxt定义的网络模型进行解析，生成内部的CanonicalAST数据结构，这部分在compiler目录下的AST.cpp和CanonicalAST.cpp两个文件里进行实现。但CanonicalAST只是一种过渡的表示，下面紧接着会执行从CanonicalAST到EngineAST的变换，后续的所有AST变换与优化都是针对于EngineAST进行的，感觉这个AST才是整个nvdla编译框架的中间IR表示。

​	EngineAST生成之后，compiler会对这个中间表示做各种变换与优化，这一步的结果就是要得到一个适合后端代码生成的AST表示。

​	最后一步就是根据变换和优化之后的EngineAST数据结构进行代码生成。这个阶段最终要的一项工作就是要解决tensor内存分配的问题，这个工作在memroyResolver阶段完成。

### 4.3.2.compiler执行流程

![](https://github.com/zeasa/nvdla-compiler/raw/master/document/imgs/compiler_flowchart.png)

1. main()函数是compiler的入口，主要功能是处理compiler命令行参数以及调用launchTest()，下表列出命令行参数

   ```
   Usage: %s [-options] --prototxt <prototxt_file> --caffemodel <caffemodel_file>
   where options include:
   -h                                              print this help message
   -o <outputpath>                                 outputs wisdom files in 'outputpath' directory
   --profile <basic|default|performance|fast-math> computation profile (default: fast-math)
   --cprecision <fp16|int8>                          compute precision (default: fp16)
   --configtarget <opendla-full|opendla-large|opendla-small>   target platform (default: nv_full)
   --calibtable <int8 calib file>                  calibration table for INT8 networks (default: 0.00787)
   --quantizationMode <per-kernel|per-filter>      quantization mode for INT8 (default: per-kernel)
   --batch                                           batch size (default: 1)
   --informat <ncxhwx|nchw|nhwc>                     input data format (default: nhwc)
   ```
   从命令函参数可以看出，目前nvdla的compiler只支持caffe模型，量化精度支持INT8和fp16，并且可以支持multibatch

2. launchTest()


   ```c
   TestInfo testInfo;
   PROPAGATE_ERROR_FAIL(testSetup(appArgs, &testInfo));
   PROPAGATE_ERROR_FAIL(parseAndCompile(appArgs, &testInfo));
   ```
   这里涉及到两个重要的结构体TestAppArgs和TestInfo

   ```c
    struct TestAppArgs
    {
        std::string project;//工程文件目录
        std::string inputPath;
        std::string inputName;
        std::string outputPath;
        std::string testname;
        std::string testArgs;
        std::string prototxt; // This should be folded into testArgs
        std::string caffemodel; // This should be folded into testArgs
        std::string cachemodel; // This should be folded into testArgs

        std::string profileName; // ok here?
        std::string profileFile;
        std::string configtarget;
        std::string calibTable;
        nvdla::QuantizationMode quantizationMode;

        NvU16 numBatches;
        nvdla::DataFormat inDataFormat;
        nvdla::DataType computePrecision;

        std::map<std::string, NvF32> tensorScales;
    };
    /*其中默认参数如下，工程名称为OpenDLA，精度为INT8*/
    static TestAppArgs defaultTestAppArgs =
      {
          /* .project = */ "OpenDLA",
          /* .inputPath = */ "./",
          /* .inputName = */ "",
          /* .outputPath = */ "./",
          /* .testname = */ "",
          /* .testArgs = */ "",
          /* .prototxt = */ "",
          /* .caffemodel = */ "",
          /* .cachemodel = */ "",
          /* .profileName = */ "fast-math",
          /* .profileFile = */ "",
          /* .configtarget = */ TARGET_CONFIG_NAME,
          /* .calibtable = */ "",
          /* .quantizationMode = */ DEFAULT_QUANT_MODE,
          /* .numBatches = */ DEFAULT_BATCH_SIZE,
          /* .inDataFormat = */ DEFAULT_DATA_FMT,
          /* .computePrecision = */ nvdla::DataType::INT8
      };
    struct TestInfo
    {
        // common
        nvdla::IWisdom* wisdom;
        std::string wisdomPath;

        // parse
        std::string modelsPath;
        std::string profilesPath;
        std::string calibTablesPath;

        // runtime
        nvdla::IRuntime* runtime;
        nvdla::ILoadable* compiledLoadable;
        NvU8 *pData;
        std::string inputImagesPath;
        std::string inputLoadablePath;
        std::map<std::string, NvDlaImage*> inputImages;
        std::map<std::string, void *> inputBuffers;
        std::map<std::string, NvDlaImage*> outputImages;
        std::map<std::string, void *> outputBuffers;
        std::vector<SubmitContext*> submits;
        NvU32 timeout;
        NvU16 numBatches; // runtime's point-of-view
        NvU32 numSubmits;
    };
   ```

3. testSetup()：主要是检查输入输出文件路径有效性，删除前一次编译中间文件，新建新一次编译中间文件夹

   ```c++
   NvDlaError testSetup(const TestAppArgs* appArgs, TestInfo* i)
   {
       NvDlaError e = NvDlaSuccess;
       std::string wisdomPath = appArgs->outputPath + "wisdom.dir/";
       std::string removeCmd = "";
       std::string imagePath = "";
       NvDlaStatType stat;
       int ii = 0;
   
       // Do input paths exist?
       e = NvDlaStat(appArgs->inputPath.c_str(), &stat);
       if (e != NvDlaSuccess)
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Input path does not exist: \"%s\"", appArgs->inputPath.c_str());
   
       // Do output paths exist?
       e = NvDlaStat(appArgs->outputPath.c_str(), &stat);
       if (e != NvDlaSuccess)
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Output path does not exist: \"%s\"", appArgs->outputPath.c_str());
   
       //删除整个wisdom文件夹，这个wisdom文件夹里面放了什么文件？？
       removeCmd += "rm -rf " + wisdomPath;
       ii = std::system(removeCmd.c_str()); // This is pretty awful
       if (ii != 0)
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "system command failed: \"%s\"", removeCmd.c_str());
   	
       //建立wisdomdir
       PROPAGATE_ERROR_FAIL(NvDlaMkdir(const_cast<char *>(wisdomPath.c_str())));
   
       // Initialize TestInfo
       i->wisdom = NULL;
       i->wisdomPath = wisdomPath;
       i->pData = NULL;
   
       return NvDlaSuccess;
   fail:
       return e;
   }
   ```

   parseAndCompiler()函数：

   ```c++
   NvDlaError parseAndCompile(const TestAppArgs* appArgs, TestInfo* i)
   {
       NvDlaError e = NvDlaSuccess;
       bool isCaffe = appArgs->caffemodel != "";
   
       PROPAGATE_ERROR_FAIL(parseSetup(appArgs, i));//这个函数为空，直接返回OK
   
       NvDlaDebugPrintf("creating new wisdom context...\n");
       i->wisdom = nvdla::createWisdom();//工厂化方法，建立编译环境，这里这个wisdom是一个接口类，工厂类和工厂模式应用
       if (!i->wisdom)
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "createWisdom() failed");
   
       NvDlaDebugPrintf("opening wisdom context...\n");
       if (!i->wisdom->open(i->wisdomPath))
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "wisdom->open() failed to open: \"%s\"", i->wisdomPath.c_str());
   
       // Parse，这里这个函数负责parse caffemodel的两个输入文件
       if (isCaffe)
           PROPAGATE_ERROR_FAIL(parseCaffeNetwork(appArgs, i));
       else
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Unknown network type encountered");
   
       // Compile，下层编译实际工作
       PROPAGATE_ERROR_FAIL(compileProfile(appArgs, i));
   
       //释放network内存数据结构
       nvdla::destroyNetwork(i->wisdom->getNetwork());
   
       NvDlaDebugPrintf("closing wisdom context...\n");
       i->wisdom->close();
   fail:
       if (i->wisdom != NULL) {
           nvdla::destroyWisdom(i->wisdom); //释放wisdom数据结构
           i->wisdom = NULL;
       }
       return e;
   }
   
   NvDlaError compileProfile(const TestAppArgs* appArgs, TestInfo* i)
   {
       NvDlaError e = NvDlaSuccess;
       std::string profileName = "";
       std::string targetConfigName = "";
   
       NvDlaFileHandle file = 0;
       std::string fileName = "";
       NvU8 *buffer = 0;
       NvU64 size = 0;
   
       nvdla::ICompiler* compiler = i->wisdom->getCompiler();
       if (!compiler)
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "wisdom->getCompiler() failed");
   
       if (!(appArgs->configtarget != ""))
           ORIGINATE_ERROR_FAIL(NvDlaError_NotInitialized, "No target config found to load");
   
       targetConfigName = appArgs->configtarget;
   
       // Determine profile
       PROPAGATE_ERROR_FAIL(generateProfile(appArgs, &profileName, i));
   
       // 调用compiler的compiler函数执行实际编译动作
       NvDlaDebugPrintf("compiling profile \"%s\"... config \"%s\"...\n", profileName.c_str(), targetConfigName.c_str());
       PROPAGATE_ERROR_FAIL(compiler->compile(profileName.c_str(), targetConfigName.c_str(), &i->compiledLoadable));
   
       // 获取loadable数据结构size
       PROPAGATE_ERROR_FAIL(compiler->getLoadableImageSize(profileName.c_str(),
                                                       &size));
       if (size == 0) {
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter,
                               "Invalid size for a loadable");
       }
   	//分配内存，存放loadable的数据
       buffer = (NvU8 *) NvDlaAlloc(size);
       if (buffer == NULL) {
           ORIGINATE_ERROR_FAIL(NvDlaError_InsufficientMemory,
                               "Failed to allocate buffer for loadable");
       }
       //拷贝loadable数据，并把数据串列输出到nvdla文件
       PROPAGATE_ERROR_FAIL(compiler->getLoadableImage(profileName.c_str(), buffer));
       fileName = profileName + ".nvdla";
       PROPAGATE_ERROR_FAIL(NvDlaFopen(fileName.c_str(), NVDLA_OPEN_WRITE, &file));
       PROPAGATE_ERROR_FAIL(NvDlaFwrite(file, buffer, size));
   fail:
       NvDlaFclose(file);
       if (buffer != NULL) NvDlaFree(buffer);
       return e;
   }
   ```
generateProfile函数：
主要是通过参数信息配置生成Profile
``` c++
NvDlaError generateProfile(const TestAppArgs* appArgs, std::string* profileName, TestInfo* i)
{
    NvDlaError e = NvDlaSuccess;
    nvdla::DataFormat inDataFormat = nvdla::DataFormat::UNKNOWN;

    if (appArgs->profileName != "")
    {
        // init named profile (basic/default/performance) with default params in its constructor and exit
        PROPAGATE_ERROR_FAIL(beginWithNamedProfile(appArgs, i));
        *profileName = appArgs->profileName;
    }
    else if (appArgs->profileFile != "")
    {
        // if named profile is absent, create a default profile
        // and then populate it with params from the cfg file (overriding as necessary)
        PROPAGATE_ERROR_FAIL(beginWithCfgProfile(appArgs, i, inDataFormat));
        *profileName = appArgs->profileFile;
        *profileName = profileName->substr(0, profileName->find_last_of("."));
    }
    else
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_NotInitialized, "No profile supplied to load");
    }

    // capture profile params from command line (override the existing ones as necessary)
    inDataFormat = inDataFormat == nvdla::DataFormat::UNKNOWN ? appArgs->inDataFormat : inDataFormat;//确定输入张量格式
    PROPAGATE_ERROR_FAIL(updateProfileWithCmdLineArgs(appArgs, i, profileName->c_str(), inDataFormat));//通过输入张量格式配置信息

fail:
    return e;
}
```
其中具体更新Profile函数为：这里是通过inDataFormat和AppArgs参数解析出具体编译参数
```c++
static NvDlaError updateProfileWithCmdLineArgs
(
    const TestAppArgs* appArgs,
    TestInfo* i,
    const char* profileName,
    nvdla::DataFormat inDataFormat
)
{
    NvDlaError e = NvDlaSuccess;
    nvdla::IProfiler* profiler;
    nvdla::IProfile* profile;

    profiler = i->wisdom->getProfiler();
    if (!profiler)
        ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "wisdom->getProfiler() failed");
    profile   = profiler->getProfile(profileName);
    if (!profile)
        ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "profiler->getProfile() failed");

    PROPAGATE_ERROR_FAIL(profile->setComputePrecision(appArgs->computePrecision));//设置精度
    PROPAGATE_ERROR_FAIL(profile->setNetworkInputDataFormat(inDataFormat));//设置输入格式

    // determine input surface format
    switch(inDataFormat)
    {
        case nvdla::DataFormat::NHWC:

            if (appArgs->computePrecision == nvdla::DataType::HALF)
            {
                PROPAGATE_ERROR_FAIL(profile->setNetworkInputSurfaceFormat(nvdla::PixelFormat::A16B16G16R16_F));
            }
            else if (appArgs->computePrecision == nvdla::DataType::INT8)
            {
                PROPAGATE_ERROR_FAIL(profile->setNetworkInputSurfaceFormat(nvdla::PixelFormat::A8B8G8R8));
            }
            else
            {
                ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "NHWC and compute precision %u is not yet supported",
                                     appArgs->computePrecision.v());
            }
            break;
        case nvdla::DataFormat::NCxHWx:
        case nvdla::DataFormat::NCHW:
        case nvdla::DataFormat::UNKNOWN:    // atleast start the test with feature data format
        default:
            if (std::strcmp(appArgs->configtarget.c_str(), "opendla-small") == 0)
                PROPAGATE_ERROR_FAIL(profile->setNetworkInputSurfaceFormat(nvdla::PixelFormat::FEATURE_X8));//设置像素点格式 FEATURE_X8是INT8模式
            else
                PROPAGATE_ERROR_FAIL(profile->setNetworkInputSurfaceFormat(nvdla::PixelFormat::FEATURE));
    }

    // determine int8 cfgs
    if (appArgs->computePrecision == nvdla::DataType::INT8)
    {
        PROPAGATE_ERROR_FAIL(profile->setTensorScalingMode(nvdla::TensorScalingMode::PER_TENSOR));
        switch(appArgs->quantizationMode)
        {
            case nvdla::QuantizationMode::PER_FILTER:
                PROPAGATE_ERROR_FAIL(profile->setQuantizationMode(nvdla::QuantizationMode::PER_FILTER));
                break;
            case nvdla::QuantizationMode::PER_KERNEL:
            case nvdla::QuantizationMode::NONE: // default to per-kernel; find a way to run int8 tests w/ NONE qtzMode cleanly
            default:
                PROPAGATE_ERROR_FAIL(profile->setQuantizationMode(nvdla::QuantizationMode::PER_KERNEL));
        }
    }
    else
    {
        PROPAGATE_ERROR_FAIL(profile->setTensorScalingMode(nvdla::TensorScalingMode::NONE));
        PROPAGATE_ERROR_FAIL(profile->setQuantizationMode(nvdla::QuantizationMode::NONE));
    }

    PROPAGATE_ERROR_FAIL(profile->setNetworkOutputDataFormat(nvdla::DataFormat::NCxHWx));

    if (std::strcmp(appArgs->configtarget.c_str(), "opendla-small") == 0)
        PROPAGATE_ERROR_FAIL(profile->setNetworkOutputSurfaceFormat(nvdla::PixelFormat::FEATURE_X8));
    else
        PROPAGATE_ERROR_FAIL(profile->setNetworkOutputSurfaceFormat(nvdla::PixelFormat::FEATURE));

    if (appArgs->numBatches > 0)
        PROPAGATE_ERROR_FAIL(profile->setMultiBatchSize(appArgs->numBatches));

fail:
    return e;
}
```
4. parseCaffeNetwork()：这个函数负责解析命令行传递的编译输入model文件，包括prototxt和caffemodel，前者主要定义网络的结构和参数，后者包含train好的网络的weight和bias参数值，这里只贴出这个函数最重要的部分：

   ```c++
   static NvDlaError parseCaffeNetwork(const TestAppArgs* appArgs, TestInfo* i)
   {
       NvDlaError e = NvDlaSuccess;
       nvdla::INetwork* network = NULL;
       const nvdla::caffe::IBlobNameToTensor* b = NULL;
       nvdla::caffe::ICaffeParser* parser = nvdla::caffe::createCaffeParser();
       std::string caffePrototxtFile = appArgs->prototxt.c_str();//caffe模型的prototxt文件
       std::string caffeModelFile = appArgs->caffemodel.c_str();//caffe模型的caffemodel文件，blob格式
   	
       //这里创建网络的内存表示，主要涉及INetwork接口类和Network实现类，这里network的create使用了工厂模式
       network = nvdla::createNetwork();
       if (!network)
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "createNetwork() failed");
   	
       //parser->parse()函数负责caffe模型的解析，传递的参数是caffe模型的两个文件，输出是network类和IBlobNameTOTensor两个
       NvDlaDebugPrintf("parsing caffe network...\n");
       b = parser->parse(caffePrototxtFile.c_str(), caffeModelFile.c_str(), network);
       if (!b)
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Unable to parse caffemodel: \"%s\"", caffePrototxtFile.c_str());
   }
   ```

   对于caffemodel的具体解析在parse()函数里实现，后面章节会具体的详解，这个函数涉及了两个重要的数据结构：INetwork和Network，这里列出这两个数据结构的主要部分

   ```c++
   class INetwork
   {
   public:
       virtual ITensor* addInput(const char * name, Dims4 dimensions) = 0;
   
       //指定网络的Input和Output Tensor
       virtual bool markInput(ITensor * tensor) = 0;
       virtual void markOutput(ITensor * tensor) = 0;
   	
       //构建网络的API函数，理论上通过以下这组add函数，就可以不使用caffe模型，手工的创建一个网络，类似大多数框架提供的网络构造API函数，但NVDLA似乎没有对外开放这组接口用于手工构造网络，TVM框架就对望开放了这组接口
       virtual IConvolutionLayer *    addConvolution   (ITensor * input, int numOutputs, int paddingValue, Dims2 kernelSize,  Dims2 tlPadding, Dims2 brPadding, Dims2 stride, Dims2 dilation,
   Weights kernelWeights, Weights biasWeights, BiasMode biasMode, int numGroups) = 0;
       virtual IFullyConnectedLayer * addFullyConnected(ITensor * input, int outputSize, Weights kernelWeights, Weights biasWeights, BiasMode biasMode) = 0;
       virtual IActivationLayer *     addActivation    (ITensor * input, ActivationType type) = 0;
       virtual IPoolingLayer *        addPooling       (ITensor * input, PoolingType type,
    Dims2 windowSize, Dims2 stride, Dims2 tlPadding, Dims2 brPadding) = 0;
       virtual ILRNLayer *            addLRN           (ITensor * input, int window, float alpha, float beta, float k) = 0;
       virtual IScaleLayer *          addScale         (ITensor * input, ScaleMode mode, Weights shift, Weights scale, Weights power) = 0;
       virtual IBatchNormLayer *      addBatchNorm     (ITensor * input, BatchNormMode mode, Weights mean, Weights variance, float epsilon) = 0;
       virtual ISoftMaxLayer *        addSoftMax       (ITensor*input) = 0;
       virtual IConcatenationLayer *  addConcatenation (ITensor*const*inputs, int numInputs) = 0;
       virtual ISliceLayer *          addSlice         (ITensor*input, int numOutputs) = 0;
       virtual IDeconvolutionLayer *  addDeconvolution (ITensor * input, int numOutputs, int paddingValue, Dims2 kernelSize, Dims2 tlPadding, Dims2 brPadding, Dims2 stride, Dims2 dilation,
   Weights kernelWeights, Weights biasWeights, BiasMode biasMode, int numGroups) = 0;
       virtual IElementWiseLayer   *  addElementWise   (ITensor *input0, ITensor* input1, ElementWiseOperation op) = 0;
   
       virtual int getNumInputs()  const  = 0;
       virtual int getNumOutputs() const  = 0;
       virtual int getNumLayers()  const  = 0;
       virtual ILayer  * getLayer(int index)  const = 0;
       virtual ITensor * getOutput(int index) const = 0;
       virtual ITensor * getInput(int index)  const = 0;
       virtual void setPoolingOutputDimensionsFormula      (OutputDimensionsFormula* callback) = 0;
       virtual void setConvolutionOutputDimensionsFormula  (OutputDimensionsFormula* callback) = 0;
       virtual void setDeconvolutionOutputDimensionsFormula(OutputDimensionsFormula* callback) = 0;
       virtual OutputDimensionsFormula& getPoolingOutputDimensionsFormula()       const = 0;
       virtual OutputDimensionsFormula& getConvolutionOutputDimensionsFormula()   const = 0;
       virtual OutputDimensionsFormula& getDeconvolutionOutputDimensionsFormula() const = 0;
       //注意这三个接口函数，获取Network的输入tensors、输出tensors和层，返回是vector
       virtual const std::vector<ITensor *> & getInputs()  const = 0;
       virtual const std::vector<ILayer * > & getLayers()  const = 0;
       virtual const std::vector<ITensor *> & getOutputs() const = 0;
   };
   ```
   ```c++
   INetwork *createNetwork()
   {
       priv::NetworkFactory::NetworkPrivPair n = priv::NetworkFactory::newNetwork();
       return n.i();
   }
   
   class NetworkFactory
   {
   public:
       typedef PrivPair<INetwork *, Network*> NetworkPrivPair;
   	
       //类工厂模式，注意，以下这些函数必须是static类型
       static NetworkPrivPair newNetwork();
       static NvDlaError deleteNetwork(INetwork *network);
   
       static Network *priv(INetwork *);//通过INetwork查找关联的Network
       static INetwork *i(Network *); //通过Network查找关联的INetwork
       static INetwork *self(void *s);
   
       static INetwork *deserializeFrom(WisdomContainerEntry *);
   
   protected:
       static BiMap<INetwork *, Network *> s_priv; //BiMap双向映射数据结构方便前后两个数据相互查找
       static BiMap<void *, INetwork *> s_self; //BiMap双向映射数据结构
   
       static INetwork *deserializeNetwork(WisdomContainerEntry *);
   };
   NetworkFactory::NetworkPrivPair NetworkFactory::newNetwork()
   {
       INetwork *network;
       Network *network_priv;
       network = network_priv = new priv::Network();//实际创建的是Network类型
       if (network) {
           s_priv.insert(network, network_priv);
           s_self.insert(network, network);
       }
       return NetworkPrivPair(network, network_priv);
   }
   
   // PrivPair and PrivDiamond simplify management of the pointers necessary
   // to track public interfaces, their private implementations and derivations
   // of such which result in a diamond inheritance pattern.  These are simply
   // fancy 2 and 4-tuples implemented by std::pair and 2x same.
   // Note: with RTTI enabled this can all disappear as dynamic_cast<>()
   // would be available instead ;(
   //这个模板类实现了一个Interface类和他的一个具体实现之间相互关联的数据结构，这么做应该是为了
   //实现RTTI功能
   template <typename I, typename P>
   class PrivPair
   {
   public:
       typedef I InterfaceType;
       typedef P PrivateType;
   
       PrivPair() : m_i_priv(0, 0) { }
       PrivPair(I i, P priv) :
           m_i_priv(i, priv) { }
       PrivPair(const PrivPair &p) :
           m_i_priv(p.m_i_priv) { }
       inline bool operator !() const { return (!m_i_priv.first) || (!m_i_priv.second); }
       inline bool operator ==(const PrivPair &rhs) const { return m_i_priv == rhs.m_i_priv; }
       inline bool operator <(const PrivPair &rhs) const { return m_i_priv < rhs.m_i_priv; }
       inline I i() const      { return m_i_priv.first;  }
       inline P priv() const   { return m_i_priv.second; }
   protected:
       std::pair<I, P> m_i_priv;
   };
   ```

5. compile()

   ```c++
   //这个函数接受的参数包括，profileName，targetConfigName，ILoadable双重指针
   NvDlaError Compiler::compile(const char *tp_name, const char *target_config_name, ILoadable **peli)
   {
       NvDlaError e = NvDlaSuccess;
       //调用compileInternal()函数完成实际编译工作
       CATCH_PROPAGATE_ERROR_FAIL(
           compileInternal(tp_name, target_config_name, peli, true /*full compile*/)
       );
   fail:
       return e;
   }
   ```

   这个函数实际调用了compileInternal()函数完成实际编译工作，但涉及到了一个重要的数据接口类:ILoabable

   ```c++
   class ILoadable
   {
   public:
       enum Interface;
       enum MemoryDomain;
       enum MemoryFlags;
       enum EventOp;
       
       //以下这些struct定义了loadable文件中的一系列重要的数据结构，
       //compiler的核心功能就是把模型编译成下面这些数据结构存入loadable文件
       //runtime的核心功能就是从loadable中解析如下数据结构并提交硬件进行计算
       struct Version;
       struct MemoryListEntry;
       struct EventListEntry;
       struct TaskListEntry;
       struct SubmitListEntry;
       struct AddressListEntry;
       struct TensorDescListEntry;
       struct RelocEntry;
       struct Blob;
   
       virtual std::string getName() const = 0;
       
       virtual int getNumMemoryListEntries() const = 0;
       virtual MemoryListEntry getMemoryListEntry(NvU16 mem_id) const = 0;
       
       virtual int getNumEventListEntries() const = 0;
       virtual EventListEntry getEventListEntry(NvU16 event_id) const = 0;
       
       virtual int getNumTaskListEntries() const = 0;
       virtual TaskListEntry getTaskListEntry(NvU16 task_id) const = 0;
       
       virtual int getNumAddressListEntries() const = 0;
       virtual AddressListEntry getAddressListEntry(NvU16 i) const = 0;
       
       virtual int getNumTensorDescListEntries() const = 0;
       virtual TensorDescListEntry getTensorDescListEntry(NvU16 i) const = 0;
       
       virtual NvDlaError getNetworkDataType(DataType::UnderlyingType *) const = 0;
       
       virtual NvDlaError getNumInputTensors(int *) const = 0;
       virtual NvDlaError getInputTensorDesc(NvU16 id, ILoadable::TensorDescListEntry *) const = 0;
       
       virtual NvDlaError getNumOutputTensors(int *) const = 0;
       virtual NvDlaError getOutputTensorDesc(NvU16 id, ILoadable::TensorDescListEntry *) const = 0;
   protected:
       ILoadable();
       virtual ~ILoadable();
   };
   ```

   在ILoadable接口中列出的一系列struct很重要，穿插在整个compiler工作的各个环节，后面会专门整理出来。

6. compilerInternal()

   第一层compilerInternal()函数，接收compiler函数传递过来的profile_name和target_config_name字符串，把这两个参数转换成Profile对象和TargetConfig对象，便于下一层compilerInternal函数使用：

   ```c++
   NvDlaError Compiler::compileInternal(const char *tp_name, const char *target_config_name, ILoadable **peli, bool fullCompile)
   {
       NvDlaError e = NvDlaSuccess;
       Profiler *profiler = 0;
       ProfileFactory::ProfilePrivPair p_profile;
       Profile *profile = 0;
       TargetConfig *target_config = 0;
       vector<engine_ast::Graph *> g;
   
       if ( !m_wisdom ) ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "No wisdom available.");
   
       profiler = ProfilerFactory::priv(m_wisdom->getProfiler());
       if ( !profiler ) ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "No profiler available.");
   
       //将tp_name字符串参数转换成Profile对象
       profile = ProfileFactory::priv(profiler->getProfile(tp_name));
       if ( !profile )
       {
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Couldn't find profile to compile.");
       }
   	//将target_config_name字符串参数转换成TargetConfig对象
       target_config = TargetConfigFactory::priv(profiler->getTargetConfig(target_config_name));
       if ( !target_config )
       {
           ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Couldn't find target config to compile.");
       }
   	//调用重载的compileInternal()执行下一步编译，这里参数已经是profile和target_config对象了
       PROPAGATE_ERROR_FAIL( compileInternal(profile, target_config, peli, fullCompile) );
   fail:
       return e;
   }
   ```

   上述代码涉及到两个重要的数据结构，Profile和TargetConfig类：

   ```c++
   class Profile : public IProfile
   {
   public:
       struct GlobalParams
       {
           NvU32                   m_NwInPixelOffX;
           NvU32                   m_NwInPixelOffY;
           nvdla::DataFormat       m_NwInDataFormat;     // NCHW default
           nvdla::DataFormat       m_NwOutDataFormat;    // NCHW default
           surface::SurfaceFormat  m_NwInSurfFormat;
           surface::SurfaceFormat  m_NwOutSurfFormat;
           surface::PixelMapping   m_NwInPixelMapping;
       };
       struct CompileParams
       {
           bool    m_canCompressWeights;
           bool    m_canWinograd;
           NvU32   m_CONVWeightBanksAllotted;
           NvU32   m_CONVDataBanksAllotted;
           bool    m_canSDPPDPOnFly;
           bool    m_canSDPMergeMathOps;
           bool    m_canSDPFuseSubEngineOps;
           bool    m_canSDPBustNOPs;
           bool    m_canSDPFuseVerticalOps;
           bool    m_useCVSRAMAllocate;
           bool    m_useMemPool;
           bool    m_useReusePooledMemory;
           bool    m_copyOutDebugSurfaces;
           bool    m_useGreedyEviction;
           NvU64   m_globalDRAMSize;
           NvU64   m_localDRAMSize;
           NvU64   m_localCVSRAMSize;
           NvU32   m_multiBatchSize;
           bool    m_canIMGPostChnlExtend;
           surface::SurfacePrecision m_computePrecision;
           nvdla::TensorScalingMode  m_tensorScalingMode;
           nvdla::QuantizationMode   m_quantizationMode;
       };
   protected:
       std::string m_name;
       std::map< std::string, ILoadable *> m_loadablesByName;
       std::vector<ILoadable *> m_loadables;
   
       GlobalParams m_globalParams;
       CompileParams m_compileParams;
   };
   ```

   这个Profile类主要是记录编译器的各种编译选项，其中有一部分应该是从命令行参数传递过来的。

   ```c++
   class TargetConfig : public ITargetConfig
   {
   public:
       struct TargetConfigParams
       {
           NvU32   m_atomicCSize;
           NvU32   m_atomicKSize;
           NvU32   m_memoryAtomicSize;
           NvU32   m_numConvBufBankAllotted;
           NvU32   m_numConvBufEntriesPerBank;
           NvU32   m_numConvBufEntryWidth;
           NvU32   m_maxBatchSize;
           bool    m_isWinogradCapable;
           bool    m_isCompressWeightsCapable;
           bool    m_isBatchModeCapable;
           bool    m_isPDPCapable;
           bool    m_isCDPCapable;
           bool    m_isSDPBiasCapable;
           bool    m_isSDPBatchNormCapable;
           bool    m_isSDPEltWiseCapable;
           bool    m_isSDPLutCapable;
           bool    m_isBDMACapable;
           bool    m_isRubikCapable;
       };
   protected:
       std::string m_instance_name;
       TargetConfigParams m_targetConfigParams;
   };
   ```

   这个TargetConfig数据结构主要用来记录NVDLA的内部硬件配置信息。

7. compilerInternal()

    这个函数是整个编译器的核心部分，主要包括了caffe模型到内部表示IR的转换，IR的各种优化变换，IR到后端代码生成等，后面会详细说明内部执行流程。

8. canonical_ast::generateGraph(), engine_ast::generateGraph(), emit()

    canonical_ast::generateGraph()功能是caffe模型到内部graph的变换，engine_ast::generateGraph()功能是内部graph到适配DPU的op的内部graph变换，emit()功能是后端代码生成，这三个函数是compilerInternal()的核心部分，剩余的其他函数主要执行graph的各种变换与优化，后面会详细分析。

### 4.3.3.代码流程分析-前端caffe模型到network内部表示

​	这部分功能实现在sw\umd\core\src\compiler\caffe\CaffeParser.cpp文件的CaffeParser::parse()函数当中。首先是几个数据结构：

```c++
class BlobNameToTensor : public IBlobNameToTensor
{
public:
    virtual void add(const std::string& name, ITensor* tensor);
    virtual ITensor* find(const char* name) const;
    virtual ITensor*& operator[](const std::string& name);
    virtual void setTensorNames();
    virtual ~BlobNameToTensor();
private:
    std::map<std::string, ITensor*> mMap;//proto文档当中的blob数据名称到Tensor的映射Map
};
//这个数据结构用来描述proto文件当中的blob数据
class BinaryProtoBlob : public IBinaryProtoBlob
{
public:
    BinaryProtoBlob(void* memory, DataType type, Dims4 dimensions);
    const void*	getData();
    Dims4 getDimensions();
    void	destroy();
protected:
    void* mMemory;//blob数据的实际内存地址
    DataType mDataType;//blob里存放的数据类型:FP32,FP16,INT16,INT8,UINT8,UINT16等
    Dims4 mDimensions;//数据格式NCHW等
    virtual ~BinaryProtoBlob();
};
class CaffeParser : public ICaffeParser
{
public:
    CaffeParser() : ICaffeParser(), mDeploy(NULL), mModel(NULL), mTmpAllocs(), mDimsCallback(NULL),
        mBlobNameToTensor(NULL), mProtobufBufferSize(1024 << 20)
    { }
    virtual const IBlobNameToTensor* parse(const char* deploy,
                                           const char* model,
                                           INetwork* network);
    virtual int identifyOutputs(INetwork * network);
    virtual ~CaffeParser();
    void setProtobufBufferSize(size_t size) { mProtobufBufferSize = size; }
    // read a blob from a protobuf file (typically a mean blob)
    static BinaryProtoBlob* parseBinaryProto(const char* fileName);
    static void shutdownProtobufLibrary();
private:
    ditcaffe::NetParameter * mDeploy;//
    ditcaffe::NetParameter * mModel;
    std::vector<void*> mTmpAllocs;
    INetwork::OutputDimensionsFormula* mDimsCallback;
    IBlobNameToTensor* mBlobNameToTensor;
    size_t mProtobufBufferSize;
};
```

要理解Caffemodel的parse，就需要了解caffe的model文件格式。前面讲了compiler的输入caffe文件包括了prototxt文件和caffemodel文件，其中prototxt文件时JSON格式的文本，主要描述了caffe网络的层次结构，那么caffemodel文件主要是存储了pre_trained的网络weight和bias参数信息。其中caffemodel文件是google的protobuf格式，其解析需要使用到protobuf库来进行。所有关于caffe模型解析的文件都位于sw/umd/core/src/compiler/caffe/目录下，其中此目录下的CaffeParser.cpp是caffemodel的解析器，其功能是调用ditcaffe文件夹下的文件完成的。ditcaffe文件夹下的ditcaffe.proto是caffemodel文件的proto结构定义文件，通过protobuf的编译器编译成protobuf-2.6.1目录下的ditcaffe.pb.cpp和ditcaffe.pb.h两个文件，即是实际caffemodel文件解析功能的具体实现。注意protobuf库解析过的caffemodel的内存变量格式是NetParameter类型，这个类型的实际定义来源于ditcaffe.proto文件定义。

```protobuf
syntax = "proto2";
//option optimize_for = LITE_RUNTIME;
package ditcaffe;
// Specifies the shape (dimensions) of a Blob.
message BlobShape {
  repeated int64 dim = 1 [packed = true];
}
message BlobProto {
  optional BlobShape shape = 7;
  repeated float data = 5 [packed = true];
  repeated float diff = 6 [packed = true];
  repeated double double_data = 8 [packed = true];
  repeated double double_diff = 9 [packed = true];
  repeated uint32 half_data = 10 [packed = true];
  repeated uint32 half_diff = 11 [packed = true];

  // 4D dimensions -- deprecated.  Use "shape" instead.
  optional int32 num = 1 [default = 0];
  optional int32 channels = 2 [default = 0];
  optional int32 height = 3 [default = 0];
  optional int32 width = 4 [default = 0];
}
```

上面这段代码就是ditcaffe.proto文件的开头部分，主要是定义了caffemodel文件里的数据存放格式。

```c++
const IBlobNameToTensor* CaffeParser::parse(const char* deployFile,const char* modelFile,
                                            INetwork * network)
{
    CHECK_NULL_RET_NULL(deployFile);
    CHECK_NULL_RET_NULL(modelFile);
    assert(mDimsCallback == 0);

    if (!mDimsCallback) {
        mDimsCallback = new CaffeParserPoolingDimsCallback;
    }
    network->setPoolingOutputDimensionsFormula(mDimsCallback);

    //调用readBinaryProto()函数解析modelFile文件，返回到NetParameter类型的mModel变量当中
    //modelFile=lenet_iter_10000.caffemodel
    //ditcaffe::NetParameter * mModel，这个NetParameter数据结构是从ditcaffe.proto自动生成的
    mModel = new dc::NetParameter();
    if (!readBinaryProto(mModel, modelFile, mProtobufBufferSize)) {
        gLogError << "Could not parse model file" << std::endl; return 0;
    }
    
    // There are some challenges associated with importing caffe models. One is that
	// a .caffemodel file just consists of layers and doesn't have the specs for its
	// input and output blobs.So we need to read the deploy file to get the input
	//readTextProto()函数解析deployFile文件，返回到NetParameter类型的mDeploy变量当中
    //deployFile=lenet.prototxt
    //ditcaffe::NetParameter * mDeploy，这个NetParameter数据结构是从ditcaffe.proto自动生成的
    mDeploy = new dc::NetParameter();
    if (!readTextProto(mDeploy, deployFile)) {
        gLogError << "Could not parse deploy file" << std::endl; return 0;
    }

    bool ok = true;
    //提取mModel中的weight数据，放到weights变量中，后面调用每层解析函数时作为参数传递进去
    CaffeWeightFactory weights(*mModel, false, mTmpAllocs);
	//mBlobNameToTensor变量维护一个blob文件中weight数据到ITensor*的映射关系
    mBlobNameToTensor = new BlobNameToTensor();
	
    //input blob只在prototxt文件当中，所以这里以mDeploy为基础给network增加inputTensor
    for (int i = 0; i < mDeploy->input_size(); i++) {
        Dims4 dims;
        if (mDeploy->input_shape_size()) {
            dims.n = (int)mDeploy->input_shape().Get(i).dim().Get(0);
            dims.c = (int)mDeploy->input_shape().Get(i).dim().Get(1);
            dims.h = (int)mDeploy->input_shape().Get(i).dim().Get(2);
            dims.w = (int)mDeploy->input_shape().Get(i).dim().Get(3);
        }
        else { // deprecated, but still used in a lot of networks
            dims.n = (int)mDeploy->input_dim().Get(i * 4 + 0);
            dims.c = (int)mDeploy->input_dim().Get(i * 4 + 1);
            dims.h = (int)mDeploy->input_dim().Get(i * 4 + 2);
            dims.w = (int)mDeploy->input_dim().Get(i * 4 + 3);
        }
        //调用network的API增加network的一个InputTensor
        //这里加入一个tensor只需要指定tensor的name和dims即可
        ITensor* tensor = network->addInput(mDeploy->input().Get(0).c_str(), dims);
        //建立network中新增InputTensor到blob文件中相应区域的name的cstring映射
        mBlobNameToTensor->add(mDeploy->input().Get(0), tensor);
    }
    
    //前面通过readBinaryProto()函数和readTextProto()函数把caffe模型的信息和weight等解析到NetParameter
  	//类型的变量mModel和mDeploy，这里通过对layer的迭代，通过NetParameter里的LayerParameter进行解析
    //逐步建立network的内存中间表示
    for (int i = 0; i < mDeploy->layer_size() && ok; i++) {
        const dc::LayerParameter& layerMsg = mDeploy->layer(i);
        if (layerMsg.has_phase() && layerMsg.phase() == dc::TEST) {
            continue;
        }
		//Dropout层处理
        if (layerMsg.type() == "Dropout")
        {
            mBlobNameToTensor->add(layerMsg.top().Get(0),
                                   mBlobNameToTensor->find(layerMsg.bottom().Get(0).c_str()));
            continue;
        }
		//Input层处理
        if (layerMsg.type() == "Input")
        {
            const dc::InputParameter& p = layerMsg.input_param();
            for (int i = 0; i < layerMsg.top_size(); i++)
            {
                const dc::BlobShape& shape = p.shape().Get(i);
                Dims4 dims(shape.dim().Get(0), shape.dim().Get(1), shape.dim().Get(2), shape.dim().Get(3));
                //调用network的API，增加Input层
                ITensor* tensor = network->addInput(layerMsg.top(i).c_str(), dims);
                mBlobNameToTensor->add(layerMsg.top().Get(i), tensor);
            }
            continue;
        }
        //Flatten层处理
        if (layerMsg.type() == "Flatten")
        {
            ITensor* tensor = (*mBlobNameToTensor)[layerMsg.bottom().Get(0)];
            (*mBlobNameToTensor)[layerMsg.top().Get(0)] = tensor;
            std::cout << "Warning: Flatten layer ignored." << std::endl;
            continue;
        }
	
        //根据layerMsg.type()信息在gParseTable中找到相应的layer层解析函数
        LayerParseFnMap::iterator v = gParseTable.find(layerMsg.type());
        if (v == gParseTable.end())
        {
            gLogError << "could not parse layer type " << layerMsg.type() << std::endl;
            ok = false;
        }
        else
        {
            //如果找到相应的layer层解析函数，则直接调用相应的解析函数对层进行解析？
            //weights变量包含了所有层的weight数据，解析层的时候可以用上
            ILayer* layer = (*v->second)(network, layerMsg, weights, mBlobNameToTensor);
            if (layer == 0)
            {
                gLogError << "error: parsing layer type " << layerMsg.type() <<
                    " index " << i << std::endl;
                ok = false;
            }
            else
            {
                layer->setName(layerMsg.name().c_str());
                mBlobNameToTensor->add(layerMsg.top(0), layer->getOutput(0));
            }
        }
    }
    //为表格中每个tensor设定name，其实就是把tensor的name设定成blobname
    mBlobNameToTensor->setTensorNames();
    return ok && weights.isOK() ? mBlobNameToTensor : 0;
}
//上面的函数用到了BlobNameToTensor的class，这个class实现了一个string到ITensor*的映射map数据结构
class BlobNameToTensor : public IBlobNameToTensor
{
public:
    virtual void add(const std::string& name, ITensor* tensor);
    virtual ITensor* find(const char* name) const;
    virtual ITensor*& operator[](const std::string& name);
    virtual void setTensorNames();
    virtual ~BlobNameToTensor();
private:
    std::map<std::string, ITensor*> mMap; //blobName到ITensor*的映射map
};
```

```protobuf
message NetParameter {
  optional string name = 1; // consider giving the network a name
  // DEPRECATED. See InputParameter. The input blobs to the network.
  repeated string input = 3;
  // DEPRECATED. See InputParameter. The shape of the input blobs.
  repeated BlobShape input_shape = 8;
  // 4D input dimensions -- deprecated.  Use "input_shape" instead.
  // If specified, for each input blob there should be four
  // values specifying the num, channels, height and width of the input blob.
  // Thus, there should be a total of (4 * #input) numbers.
  repeated int32 input_dim = 4;
  // Whether the network will force every layer to carry out backward operation.
  // If set False, then whether to carry out backward is determined
  // automatically according to the net structure and learning rates.
  optional bool force_backward = 5 [default = false];
  // The current "state" of the network, including the phase, level, and stage.
  // Some layers may be included/excluded depending on this state and the states
  // specified in the layers' include and exclude fields.
  optional NetState state = 6;
  // Print debugging information about results while running Net::Forward,
  // Net::Backward, and Net::Update.
  optional bool debug_info = 7 [default = false];
  // The layers that make up the net.  Each of their configurations, including
  // connectivity and behavior, is specified as a LayerParameter.
  repeated LayerParameter layer = 100;  // ID 100 so layers are printed last.
  // DEPRECATED: use 'layer' instead.
  repeated V1LayerParameter layers = 2;
}
message LayerParameter {
  optional string name = 1; // the layer name
  optional string type = 2; // the layer type
  repeated string bottom = 3; // the name of each bottom blob
  repeated string top = 4; // the name of each top blob
  // The train / test phase for computation.
  optional Phase phase = 10;
  // The amount of weight to assign each top blob in the objective.
  // Each layer assigns a default value, usually of either 0 or 1,
  // to each top blob.
  repeated float loss_weight = 5;
  // Specifies training parameters (multipliers on global learning constants,
  // and the name and other settings used for weight sharing).
  repeated ParamSpec param = 6;
  // The blobs containing the numeric parameters of the layer.
  repeated BlobProto blobs = 7;
  // Specifies whether to backpropagate to each bottom. If unspecified,
  // Caffe will automatically infer whether each input needs backpropagation
  // to compute parameter gradients. If set to true for some inputs,
  // backpropagation to those inputs is forced; if set false for some inputs,
  // backpropagation to those inputs is skipped.
  // The size must be either 0 or equal to the number of bottoms.
  repeated bool propagate_down = 11;
  // Rules controlling whether and when a layer is included in the network,
  // based on the current NetState.  You may specify a non-zero number of rules
  // to include OR exclude, but not both.  If no include or exclude rules are
  // specified, the layer is always included.  If the current NetState meets
  // ANY (i.e., one or more) of the specified rules, the layer is
  // included/excluded.
  repeated NetStateRule include = 8;
  repeated NetStateRule exclude = 9;
  // Parameters for data pre-processing.
  optional TransformationParameter transform_param = 100;
  // Parameters shared by loss layers.
  optional LossParameter loss_param = 101;
  // Layer type-specific parameters.
  //
  // Note: certain layers may have more than one computational engine
  // for their implementation. These layers include an Engine type and
  // engine parameter for selecting the implementation.
  // The default for the engine is set by the ENGINE switch at compile-time.
  optional AccuracyParameter accuracy_param = 102;
  optional ArgMaxParameter argmax_param = 103;
  optional BatchNormParameter batch_norm_param = 139;
  optional BiasParameter bias_param = 141;
  optional ConcatParameter concat_param = 104;
  optional ContrastiveLossParameter contrastive_loss_param = 105;
  optional ConvolutionParameter convolution_param = 106;
  optional CropParameter crop_param = 144;
  optional DataParameter data_param = 107;
  optional DropoutParameter dropout_param = 108;
  optional DummyDataParameter dummy_data_param = 109;
  optional EltwiseParameter eltwise_param = 110;
  optional ELUParameter elu_param = 140;
  optional EmbedParameter embed_param = 137;
  optional ExpParameter exp_param = 111;
  optional FlattenParameter flatten_param = 135;
  optional HDF5DataParameter hdf5_data_param = 112;
  optional HDF5OutputParameter hdf5_output_param = 113;
  optional HingeLossParameter hinge_loss_param = 114;
  optional ImageDataParameter image_data_param = 115;
  optional InfogainLossParameter infogain_loss_param = 116;
  optional InnerProductParameter inner_product_param = 117;
  optional InputParameter input_param = 143;
  optional LogParameter log_param = 134;
  optional LRNParameter lrn_param = 118;
  optional MemoryDataParameter memory_data_param = 119;
  optional MVNParameter mvn_param = 120;
  optional ParameterParameter parameter_param = 145;
  optional PoolingParameter pooling_param = 121;
  optional PowerParameter power_param = 122;
  optional PReLUParameter prelu_param = 131;
  optional PythonParameter python_param = 130;
  optional ReductionParameter reduction_param = 136;
  optional ReLUParameter relu_param = 123;
  optional ReshapeParameter reshape_param = 133;
  optional ScaleParameter scale_param = 142;
  optional SigmoidParameter sigmoid_param = 124;
  optional SoftmaxParameter softmax_param = 125;
  optional SPPParameter spp_param = 132;
  optional SliceParameter slice_param = 126;
  optional TanHParameter tanh_param = 127;
  optional ThresholdParameter threshold_param = 128;
  optional TileParameter tile_param = 138;
  optional WindowDataParameter window_data_param = 129;
}
```

​	这个函数中，有用到gParseTable这个层解析函数表，表格中存放的是从caffe模型中读取的各个层的对应解析函数表：

```c++
LayerParseFnMap::value_type gParseTableData[] =
{
        LayerParseFnMap::value_type("Convolution", parseConvolution),
        LayerParseFnMap::value_type("Pooling", parsePooling),
        LayerParseFnMap::value_type("InnerProduct", parseInnerProduct),
        LayerParseFnMap::value_type("ReLU", parseReLU),
        LayerParseFnMap::value_type("Softmax", parseSoftMax),
        LayerParseFnMap::value_type("SoftmaxWithLoss", parseSoftMax),
        LayerParseFnMap::value_type("LRN", parseLRN),
        LayerParseFnMap::value_type("Power", parsePower),
        LayerParseFnMap::value_type("Eltwise", parseEltwise),
        LayerParseFnMap::value_type("Concat", parseConcat),
        LayerParseFnMap::value_type("Deconvolution", parseDeconvolution),
        LayerParseFnMap::value_type("Sigmoid", parseSigmoid),
        LayerParseFnMap::value_type("TanH", parseTanH),
        LayerParseFnMap::value_type("BatchNorm", parseBatchNormalization),
        LayerParseFnMap::value_type("Scale", parseScale)
};
const int nelems = sizeof gParseTableData / sizeof gParseTableData[0];
LayerParseFnMap gParseTable( gParseTableData, gParseTableData + nelems);

typedef ILayer*(*LayerParseFn)(INetwork *, const dc::LayerParameter&, CaffeWeightFactory&,
                                      IBlobNameToTensor *);
```

​	可以看到，对应caffe模型中的每一种layer，都有相应的解析函数，这些解析函数的功能都类似，负责解析一个layer，然后调用network提供的API，自动构造一个network网络内存模型。整个caffe模型到network内存表示的解析比较复杂，其中用到了google开源的protobuf库，实现在CaffePaser.cpp文件当中。

### 4.3.4.代码流程分析-network内部表示到canonical_ast::Graph图表示

前一阶段主要工作是使用protobuf库，根据ditcaffe.proto文件的定义，解析compiler的输入文件*.prototxt和*.caffemodel，生成protobuf的deserialize格式数据NetParameter，然后根据NetParameter数据（包括net的层定义和weight等信息），根据每层的type调用network类的各种API构建一个network内存表示对象，如下：

```c++
class Network : public INetwork
{
public: // externally facing

    virtual ITensor* addInput(const char* name, Dims4 dimensions);

    //	virtual void markChanged(const ILayer*);
    virtual bool markInput(ITensor * tensor);
    virtual void markOutput(ITensor* tensor);

    //下面是从INetwork接口继承过来的network构造用的API函数
    virtual IConvolutionLayer *    addConvolution(ITensor* input, int numOutputs, int paddingValue,
Dims2 kernelSize, Dims2 tlPadding, Dims2 brPadding, Dims2 stride, Dims2 dilation, Weights kernelWeights, Weights biasWeights, BiasMode biasmode, int numGroups);
    virtual IFullyConnectedLayer * addFullyConnected(ITensor* input, int outputSize, Weights kernelWeights, Weights biasWeights, BiasMode biasMode);
    virtual IActivationLayer *     addActivation(ITensor* input, ActivationType type);
    virtual IPoolingLayer *        addPooling(ITensor* input, PoolingType type,Dims2 windowSize, Dims2 stride, Dims2 tlPadding, Dims2 brPadding);
    virtual ILRNLayer *            addLRN(ITensor* input, int window, float alpha, float beta, float k);
    virtual IScaleLayer *          addScale(ITensor* input, ScaleMode mode, Weights shift, Weights scale, Weights power);
    virtual IBatchNormLayer *      addBatchNorm(ITensor* input, BatchNormMode mode, Weights mean, Weights variance, float epsilon);
    virtual ISoftMaxLayer *        addSoftMax(ITensor* input);
    virtual IConcatenationLayer *  addConcatenation(ITensor * const * inputs, int numInputs);
    virtual ISliceLayer *          addSlice(ITensor* input, int numOutputs);
    virtual IDeconvolutionLayer *  addDeconvolution(ITensor* input, int numOutputs, int paddingValue,
Dims2 kernelSize, Dims2 tlPadding, Dims2 brPadding, Dims2 stride, Dims2 dilation,Weights kernelWeights, Weights biasWeights, BiasMode biasMode, int numGroups);
    virtual IElementWiseLayer *    addElementWise(ITensor* input0, ITensor* input1, ElementWiseOperation op);

    virtual int  getNumInputs() const;
    virtual int  getNumOutputs() const;
    virtual int  getNumLayers() const ;

    virtual ILayer  * getLayer(int index)  const;
    virtual ITensor * getOutput(int index) const;
    virtual ITensor * getInput(int index)  const;

    virtual void setPoolingOutputDimensionsFormula      (OutputDimensionsFormula* callback);
    virtual void setConvolutionOutputDimensionsFormula  (OutputDimensionsFormula* callback);
    virtual void setDeconvolutionOutputDimensionsFormula(OutputDimensionsFormula* callback);

    virtual OutputDimensionsFormula& getPoolingOutputDimensionsFormula()       const;
    virtual OutputDimensionsFormula& getConvolutionOutputDimensionsFormula()   const;
    virtual OutputDimensionsFormula& getDeconvolutionOutputDimensionsFormula() const;

    virtual const std::vector<ITensor *>& getInputs()  const;
    virtual const std::vector<ILayer * >& getLayers()  const;
    virtual const std::vector<ITensor *>& getOutputs() const;

    virtual NvU16 getFactoryType() const;
public: // internally facing
    Network();
    virtual ~Network();
    virtual bool serializeTo(WisdomContainerEntry *) const;
    virtual bool deserializeFrom(WisdomContainerEntry *);
    virtual bool assignSymbols(Wisdom *);

protected:
    friend class Wisdom;
    friend class NetworkFactory;
    void destroy();
private:
    std::string newLayerName() const;
    std::string newTensorName() const;
    ITensor* addTensor(const std::string & s);
    const ILayer* findLayer(const std::string& name) const;
    bool checkNames(const char* name);

    std::vector<ITensor *> mTensors;//network的tensor
    std::vector<ILayer *>  mLayers; //network的layers
    std::vector<ITensor *> mInputs; //network的inputTensor
    std::vector<ITensor *> mOutputs;//network的outputTensor

    // provides layer dimension caching. Layers can be mutated in any order and dimensions queried at any point.
    // So mutating a layer trims this, and querying always refills the cache up to the queried layer
    //	mutable std::vector<Dims3> mDimensions;

    // internal flags used by the builder that are not accessible through the API
    // int mInternalBuildFlags{ InternalBuildFlags::kENABLE_GRAPH_OPTIMIZATIONS };
    OutputDimensionsFormula* mConvDims, *mDeconvDims, *mPoolDims;
};
```

可以看到，除了一系列各种type的layer添加API函数以外，还有就是下列几个private数据变量：

```c++
    std::vector<ITensor *> mTensors;//network的tensor
    std::vector<ILayer *>  mLayers; //network的layers
    std::vector<ITensor *> mInputs; //network的inputTensor
    std::vector<ITensor *> mOutputs;//network的outputTensor
```

可以看到，这几个变量只是简单的记录了network的layer、tensor、input和output等信息，并没有图的节点边缘以及连接先后关系等概念。下一阶段应该是根据network数据结构构建CAG图的工作。

​	从network内部表示到canonical_ast::Graph图表示，这一部分功能主要是由canonical_ast::generateGraph()这个函数完成的，输入是一个network对象，只有layer和tensor概念，输出就变成一个canonical_ast::Graph图对象，有了node和edge的概念，下面分析canonical_ast::generateGraph()函数代码：

```c++
canonical_ast::Graph *canonical_ast::generateGraph(Network *network)
{
    vector<canonical_ast::Edge *> input_edges;//graph的输入edges
    vector<canonical_ast::Edge *> output_edges;//graph的输出edges
	
    //network中的layer和Graph中的node的映射map
    map<canonical_ast::Node *, Layer *, Graph::nodeCompareFn>  node_layer;
    map<canonical_ast::Node *, Layer *, Graph::nodeCompareFn>::iterator lni;

    map<Tensor *, canonical_ast::Edge *>  tensor_edge;//nework中tensor和Graph中Edge的映射MAP
    map<Tensor *, Tensor *>  nw_tensor_to_can_tensor;//network中的tensor和Graph中的tensor的映射MAP
    map<Tensor *, canonical_ast::Edge *>::iterator tei;

    Graph *graph = new Graph();//新建一个canonical_ast::Graph
	
    //下面这个循环把network中的inputTensor汇总成一个数组，并把Graph中input_edges数组大小设定成
    //network中的inputTensor的数组大小
    vector<Tensor *> network_inputs;
    for (int ni = 0; ni < network->getNumInputs(); ++ni)
    {
        network_inputs.push_back(TensorFactory::priv(network->getInput(ni)));
    }
    input_edges.resize(network_inputs.size());

    //下面这个循环把network中的outputTensor汇总成一个数组，并把Graph中outputedges数组大小设定成
    //network中的outputTensor的数组大小
    vector<Tensor *> network_outputs;
    for (int ni = 0; ni < network->getNumOutputs(); ++ni)
    {
        network_outputs.push_back(TensorFactory::priv(network->getOutput(ni)));
    }
    output_edges.resize(network_outputs.size());

    //下面这个循环迭代network中的layer序列，根据每个layer的信息分别建立Graph中的相应的Node
    for (int li = 0; li < network->getNumLayers(); li++)
    {
        ILayer *ilayer = network->getLayer(li);
        Layer *layer = LayerFactory::priv(ilayer);
        if ( !(ilayer && layer) )
        {
            gLogError << __func__ << "encountered null layer at network layer index=" << li << endl;
            continue;
        }
		
        //根据network中的layer，建立相应的Node
        canonical_ast::Node *can_node = newCanonicalNode(layer);
        if ( !can_node )
        {
            delete graph; // blow up
            graph = 0;
            goto done;
        }
        can_node->setGraph(graph);//指定node的container是graph
        graph->insertNode(can_node);//把node加入graph的node序列当中

        can_node->setId(graph->nextNodeId());//设定node的id序号，string类型，例如n-0,n-1等递增的
        can_node->setName(layer->getName());//node的name设定成network中对应layer的name
        
		//在node_layer映射map中添加一项，记录graph中node和network中对应layer的对应关系
        node_layer[can_node] = layer;
    }

    //现在，所有network中的layer都在graph中建立了相应的node，并且这个对应关系也记录在了node_layer的MAP中
    //下面循环迭代这个MAP中的每一项
    for (lni = node_layer.begin(); lni != node_layer.end(); ++lni)
    {
        canonical_ast::Node *node = lni->first;
        Layer *l = lni->second;

        size_t input_tensors = 0, output_tensors = 0, aux_input_tensors = 0;
        vector<Tensor *> io_tensors, aux_tensors;
        NVDLA_UNUSED(aux_input_tensors);
		//针对network中当前迭代的这个layer，找出其全部inputTensors并加入io_tensors列表
        for(int ii = 0, II = l->getNumInputs(); ii < II; ++ii)
        {
            Tensor *tensor = TensorFactory::priv(l->getInput(ii));
            if ( !tensor )
            {
                gLogError << __func__ << " 3.<null>.i." << ii << endl;
                continue;
            }
            io_tensors.push_back(tensor);
            input_tensors++;
        }
        //针对network中当前迭代的这个layer，找出其全部outputTensors并加入io_tensors列表
        for(int oo = 0, OO = l->getNumOutputs(); oo < OO; ++oo)
        {
            Tensor *tensor = TensorFactory::priv(l->getOutput(oo));
            if ( ! tensor )
            {
                gLogError << __func__ << " 3.<null>.o." << oo << endl;
                continue;
            }
            io_tensors.push_back(tensor);
            output_tensors++;
        }
		//针对当前layer，迭代刚刚找到的全部iotensor的列表
        for(size_t io = 0, IO = io_tensors.size(); io < IO; ++io)
        {
            Tensor *nw_tensor = io_tensors[io];
            bool is_input = io < input_tensors;//根据当前tensor在列表中的位置判断是input还是output
            //edge_side是个enum值，input=SECOND，output=FIRST
            ast::EdgeSide edge_side(is_input ? ast::EdgeSideEnum::SECOND:ast::EdgeSideEnum::FIRST);
            //edge_dir是个enum值，有单向双向和无方向三种，这里统一设定为单向
            ast::EdgeDirection edge_dir(ast::EdgeDirectionEnum::DIRECTED);
		   //在tensor_edge映射MAP中查找当前tensor的对应项
            map<Tensor *, canonical_ast::Edge *>::iterator f = tensor_edge.find(nw_tensor);
            canonical_ast::Edge *can_edge = 0;//graph中的edge
            Tensor* can_tensor = 0;//graph中的tensor
            if ( f == tensor_edge.end() )//如果没有在MAP中找到对应项
            {
                can_edge = new canonical_ast::Edge();//新建一个graph中的edge
                can_edge->setGraph(graph);//把新建的edge的container设定为graph

                can_tensor = nw_tensor->clone();//把network中的tensor复制到一个新的变量can_tensor
                can_tensor->setNetwork(NULL);   //由于这个新的tensor变量将加入graph所以其network指针清空，不在指向原来的network(这里是复制一份tensor，network中原来的tensor还在)
                can_tensor->setTensorType(TensorType::kIO);//graph中的tensor设定为IO类型
                can_edge->setId(graph->nextEdgeId());//graph中edge的Id设定为string，e-0,e-1,e-2等
                can_edge->setOriginalTensor(can_tensor);//graph中的edge的原始tensor设定为can_tensor，注意，这里的OriginalTensor指向的是从network中复制clone过来的一个副本，并不在network中，可以看出这里的包含关系，graph-->can_edge-->can_tensor
                graph->insertEdge(can_edge);//把根据network中1个layer的iotensor新建的edge加入graph列表
			  
                tensor_edge[nw_tensor] = can_edge;//tensor_edge映射MAP加入nw中tensor到graph中edge映射
                //nw_tensor_to_can_tensor映射MAP加入nw中tensor到graph中edge的tensor映射
                nw_tensor_to_can_tensor[nw_tensor] = can_tensor;
            } else {
                can_edge = f->second;
            }
            //把当前新建的edge加入到node的edge_side侧列表当中
            graph->appendNodeToEdge(can_edge, edge_side, node);

            // if this is an input node it could be one of the network inputs.
            // if so keep track of it.
            if ( is_input )
            {
                //迭代整个network的inputTensors列表
                for ( size_t iti = 0; iti < network_inputs.size(); iti++)
                {
                    //如果当前node对应的这个inputTensor在整个network的inputTensors列表当中
                    if ( nw_tensor == network_inputs[iti] )
                    {
                        input_edges[iti] = can_edge;//把当前edge加入graph的input_edges列表当中
                        can_tensor = nw_tensor_to_can_tensor[nw_tensor];
                        //设定当前tensor属性为INPUT
                        can_tensor->setTensorType(TensorType::kNW_INPUT);
                        break;
                    }
                }
                node->markInputEdge(can_edge);//告诉当前node，你的这个edge是一个网络inputedge
            }
            else
            {
                //这部分解释参考上面
                for ( size_t oti = 0; oti < network_outputs.size(); oti++)
                {
                    if ( nw_tensor == network_outputs[oti] )
                    {
                        output_edges[oti] = can_edge;
                        can_tensor = nw_tensor_to_can_tensor[nw_tensor];
                        can_tensor->setTensorType(TensorType::kNW_OUTPUT);
                        break;
                    }
                }
                node->markOutputEdge(can_edge);
            }
        }
    }

    if ( input_edges.size() )
    {
        graph->setInputEdges(input_edges);//设定整个graph的inputedges队列为input_edges
    }
    if ( output_edges.size() )
    {
        graph->setOutputEdges(output_edges);//设定整个graph的outputedges队列为input_edges
    }

    graph->scoredOrdering()->generate();//graph计分牌生成，这部分比较复杂，单独讲
    graph->markClean();//清除graph的m_dirty脏标志，所有对graph的更改都要设定m_dirty为true

done:
    return graph;//把按照network生成的graph作为返回值返回
}
```

### 4.3.5.代码流程分析-canonical_ast::Graph到engine_ast::Graph图表示

​	这部分功能主要由engine_ast::generateGraph()函数完成

```c++
//这个函数完成的是两个graph的转换，通过参数可以看到，输入不仅仅由can_graph,还有编译器的profile和编译目标配置target_config，说明转换后的graph应该反应部分硬件和编译选项的要求
engine_ast::Graph *engine_ast::generateGraph(Profile *profile, TargetConfig *target_config, canonical_ast::Graph *can_graph)
{
    NvDlaError e = NvDlaSuccess;
    vector<engine_ast::Edge *> input_edges;
    vector<engine_ast::Edge *> output_edges;

    vector<canonical_ast::Node *> can_edge_first_nodes, can_edge_second_nodes;
    map<canonical_ast::Node *, engine_ast::Node *> can_to_eng_sink_node_map;
    map<canonical_ast::Node *, engine_ast::Node *> can_to_eng_source_node_map;
    map<canonical_ast::Edge *, engine_ast::Edge *> can_to_eng_edge_map;
    vector<canonical_ast::Node *>::const_iterator f, begin, end;
    vector<engine_ast::Node *> first_nodes, second_nodes;
    engine_ast::Graph *eng_graph;

    if ( !profile )
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "must associate profile with Engine AST generateGraph");
    }

    if ( !target_config )
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "must associate target_config with Engine AST generateGraph");
    }
	
    //编译目标是否支持批处理
    if (target_config->isBatchModeCapable())
    {
        NvU32 numBatches = profile->multiBatchSize();
        NvU32 maxBatches = target_config->maxBatchSize();
		//如果指定编译的批处理batchsize大于目标能力
        if (numBatches > maxBatches)
        {
            ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "numbatches is greater than allowed maxbatches (%d)", maxBatches);
        }
    }
	//建立engine_graph对象，参数是profile和target_config
    eng_graph  = new engine_ast::Graph(profile, target_config);
    if ( !eng_graph )
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_InsufficientMemory, "Can't create a new Engine AST");
    }
	//初始化eng_graph的资源，主要是内存池和LutManager，内存池包括GLOBAL_DRAM_POOL，LOCAL_DRAM_POOL
    //如果profile开启了SRAM，那么还有LOCAL_CVSRAM_POOL，这三个mempool的大小由profile参数指定
    e = eng_graph->initGraphResources();
    if (e != NvDlaSuccess)
    {
        delete eng_graph;
        eng_graph = NULL;
        ORIGINATE_ERROR_FAIL(NvDlaError_InsufficientMemory, "Couldn't initialize all graph resources");
    }
	
    //graph访问计分板，后面统一详细解释
    eng_graph->setScoredOrdering( new ScoredDependencyOrdering(eng_graph) );
    eng_graph->setOrdering(new DependencyOrdering(eng_graph->scoredOrdering()));

    // create edges to mirror the canonical edges.
    // 迭代所有can_graph的edges，建立相应的engine_edge,并把两者关联加入MAP
    for ( set<canonical_ast::Edge *>::iterator cei = can_graph->edges().begin(), CEI = can_graph->edges().end();
          cei != CEI; ++cei )
    {
        //根据canonical_ast::Edge建立engine_ast::Edge对象
        engine_ast::Edge* engine_edge = new engine_ast::Edge(*cei);
        Tensor* engine_tensor = 0;
        if ( !engine_edge )
        {
            delete eng_graph; // blow up
            eng_graph = NULL;
            ORIGINATE_ERROR_FAIL(NvDlaError_InsufficientMemory, "Couldn't transform canonical edge '%s' into engine edge", (*cei)->id().c_str());
        }
		//engine_tensor复制自can_tensor,前面讲过can_tensor其实是clone自network的tensor
        engine_tensor = (*cei)->originalTensor()->clone();
        engine_tensor->setDataFormat(nvdla::DataFormat::NCHW);//engine_tensor的dataformat
        engine_tensor->setNetwork(NULL); //这一步其实用不着，因为can_tensor已经是NULL了

        engine_edge->setGraph(eng_graph);//指定engine_edge的container为eng_graph
        engine_edge->setId(eng_graph->nextEdgeId());//设定engine_edge的Id，string类型，e-0,e-1等
        engine_edge->setDataEdge();//设定edge的type为DATA
        engine_edge->setOriginalTensor(engine_tensor);//指定edge关联的tensor
        can_to_eng_edge_map[*cei] = engine_edge;//建立can_edge和engine_edge的关联MAP
        eng_graph->insertEdge(engine_edge);//把engine_edge加入eng_graph的edge列表
    }

    //如果没有指定multibatchsize，则根据network的input tensor的n指定推导multibatchsize
    //如果指定了multibatchsize，那就按照multibatchsize来执行
    if (profile->multiBatchSize() == 0)
    {
        // Patch up profile->multiBatchSize()
        // The compiler should be querying this information from the network instead of the profile
        // Collect the multibatch size of the network, based on the input tensor dimensions
        for ( vector<canonical_ast::Edge *>::const_iterator cie = can_graph->inputEdges().begin();
                    cie != can_graph->inputEdges().end(); ++cie)
        {
            //can_graph的inputedge对应的engine_graph的edge
            engine_ast::Edge *input_edge = can_to_eng_edge_map[*cie];
            //获取input_edge的tensor Dimension
            Dims4 networkDims = input_edge->originalTensor()->getDimensions();
		   //根据input_edge的tensor Dimension的n，设定profile的multibatchsize
            PROPAGATE_ERROR_FAIL(profile->setMultiBatchSize(networkDims.n));
        }
    }

    // create nodes to mirror the canonical nodes
    // 迭代can_graph的所有nodes
    for ( set<canonical_ast::Node *>::iterator cni = can_graph->nodes().begin(), CNI = can_graph->nodes().end();
          cni != CNI; ++cni )
    {
        engine_ast::Graph::EdgeSequence engSrcEdges;//engine_graph的SrcEdges
        engine_ast::Graph::EdgeSequence engSinkEdges;//engine_graph的SinkEdges
        engine_ast::Graph::NodeSequence engNodes;//engine_graph的Nodes
        canonical_ast::Graph::EdgeSequence canSrcEdges = can_graph->nodeEdges(*cni, ast::EdgeSideEnum::SECOND);//can_graph的当前node的inputedge的总和
        canonical_ast::Graph::EdgeSequence canSinkEdges = can_graph->nodeEdges(*cni, ast::EdgeSideEnum::FIRST);//can_graph的当前node的outputedge的总和
        canonical_ast::Graph::EdgeSequenceIterator cei;
		//找出所有canSrcEdges对应的engine_edge,放入engSrcEdges列表
        for (cei = canSrcEdges.begin(); cei != canSrcEdges.end(); ++cei)
        {
            engSrcEdges.push_back(can_to_eng_edge_map[*cei]);
        }
		//找出所有canSinkEdges对应的engine_edge,放入engSinkEdges列表
        for (cei = canSinkEdges.begin(); cei != canSinkEdges.end(); ++cei)
        {
            engSinkEdges.push_back(can_to_eng_edge_map[*cei]);
        }
		
        //从当前的can_node转化出eng_nodes，之所以是end_nodes是因为一个can_node可以对应2，3个eng_nodes
        //转换完毕是否把结果的engNodes挂在eng_graph上？？？需要详细看transformCanNode()函数代码
        e = transformCanNode(eng_graph, *cni, engSrcEdges, engSinkEdges, engNodes);
        if ( e != NvDlaSuccess )
        {
            delete eng_graph; // blow up
            eng_graph = NULL;
            ORIGINATE_ERROR_FAIL(e, "Couldn't transform canonical node '%s' into engine node", 										(*cni)->id().c_str());
        }
		
        //n-0:->n-0:dc-conv-0 n-1:bias-0 
        //n-1:->n-2:pdp-0 
        //n-2:->n-3:dc-conv-1 n-4:bias-1 
        //n-3:->n-5:pdp-1 
        //n-4:->n-6:fc-0 n-7:bias-2 
        //n-5:->n-8:sdp-scale-0 n-9:act-0 
        //n-6:->n-10:fc-1 n-11:bias-3 
        //n-7:->n-12:cpu-sm-0 
        //上面列出的就是transformCanNode()函数的转换结果，可以看到1个can_node有可能转换成2个eng_node
        //是因为can_node是直接对那个network模型的node，而在engine中，一个network模型中的node有可能是
        //需要2个engine前后协同计算才能得到结果，所有这里的eng_node其实已经是映射到硬件上的node了
        if ( eng_graph->debugGraphDump() )
        {
            gLogInfo << (*cni)->id() << ":->";
            for (vector<engine_ast::Node *>::iterator ni=engNodes.begin(); ni!=engNodes.end(); ++ni)
            {
                gLogInfo << (*ni)->id() << ":" << (*ni)->name() << " ";
            }
            gLogInfo << std::endl;
        }
    }
	
    //迭代can_graph的所有inputEdges
    for ( vector<canonical_ast::Edge *>::const_iterator cie = can_graph->inputEdges().begin();
            cie != can_graph->inputEdges().end(); ++cie)
    {
        //找出can_graph的首个inputEdge对应的eng_edge
        engine_ast::Edge *first_edge = can_to_eng_edge_map[can_graph->inputEdges().front()];
        //当前迭代的can_edge对应的eng_edge
        engine_ast::Edge *input_edge = can_to_eng_edge_map[*cie];
        //当前eng_edge对应的tensor格式设定为profile指定的InputDataFormat
        input_edge->originalTensor()->setDataFormat(profile->networkInputDataFormat());

        // 要求所有的inputedge的multibatch参数n必须一致
        if (first_edge->originalTensor()->getDimensions().n != input_edge->originalTensor()-> getDimensions().n)
        {
            ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "Input tensor multibatch dimensions mismatch: %d != %d", first_edge->originalTensor()->getDimensions().n, input_edge->originalTensor()->getDimensions().n);
        }

        Dims4 networkDims = input_edge->originalTensor()->getDimensions();
        //拿所有inputedge的multibatch参数n和profile指定的multibatch参数进行比较，如果不一致
        //则以profile指定的参数为准，并把inputedge中的tensor变量的networkDims.n更新为profile指定的值
        if ( networkDims.n != (NvS32)profile->multiBatchSize() )
        {
            gLogWarning << "Overriding input multibatch size from " << networkDims.n << " to " << profile->multiBatchSize() << endl;
            networkDims.n = profile->multiBatchSize();
            input_edge->originalTensor()->setDimensions(networkDims);
        }

        // 如果profile指定的输入IMG tensor的channel数与network提供的networkDims.c不一致
        // 则以profile设定的input tensor的channel值为准，同时更新engine_graph的inputedge对应的tensor
        // 的networkDims.c的值
        if ( profile->networkInputSurfaceFormat().category() == surface::SurfaceCategoryEnum::IMG &&
             networkDims.c != profile->networkInputSurfaceFormat().channelsPerAtom())
        {
            gLogWarning << "Prototxt #chnls (C = "
                        << networkDims.c
                        << ") != Profile #chnls for input ("
                        << profile->networkInputSurfaceFormat().c_str()
                        << ": C = "
                        << (int)profile->networkInputSurfaceFormat().channelsPerAtom()
                        << "). Preferring #chnls from Profile for compiling."
                        << endl;
            networkDims.c = profile->networkInputSurfaceFormat().channelsPerAtom();
            input_edge->originalTensor()->setDimensions(networkDims);

            // copy the tensor scales and offsets to the extra channel if any
            // transform_param {
            // scale: 0.00390625
            // mean_value: 128
            // }
            // input tensor的scale
            if (input_edge->originalTensor()->getChannelScales().size())
            {
                NvF32 tensorScale  = input_edge->originalTensor()->getChannelScales().at(0);
                std::vector<NvF32> channelScales;
                for (NvU32 cc = 0; cc < (NvU32)networkDims.c; ++cc)
                {
                    channelScales.push_back(tensorScale);
                }
                input_edge->originalTensor()->setChannelScales(channelScales);
            }
		   // input tensor的offset(mean_value)
            if (input_edge->originalTensor()->getChannelOffsets().size())
            {
                NvF32 tensorOffset = input_edge->originalTensor()->getChannelOffsets().at(0);
                std::vector<NvF32> channelOffsets;
                for (NvU32 cc = 0; cc < (NvU32)networkDims.c; ++cc)
                {
                    channelOffsets.push_back(tensorOffset);
                }
                input_edge->originalTensor()->setChannelOffsets(channelOffsets);
            }
        }
	    // 这个bindid好像只是整个图的input和output的edge才设定，这个函数只是设定两个变量而已
        // m_bindDomain = bindDomain; m_bindId = id; bingDomain有input output debug三种
        // 这个bindid也是随着inputedge的增加顺序往后排
        input_edge->setBindId(input_edges.size(), IOD_Input);
        if ( eng_graph->debugBinding() )
        {
            gLogInfo << "EngineAST graph level input edge[" << input_edges.size() << "] is " <<                             input_edge->id() << endl;
            gLogInfo << "input bind id: " << input_edge->bindId() << endl;
        }
        input_edges.push_back( input_edge );
    };
	
    // 设定整个eng_graph的inputedge列表为input_edges
    if ( input_edges.size() )
    {
        eng_graph->setInputEdges(input_edges);
    }

	//按照以上处理inputedge的方法，处理所有的outputedges
    for ( vector<canonical_ast::Edge *>::const_iterator coe = can_graph->outputEdges().begin();
            coe != can_graph->outputEdges().end(); ++coe)
    {
        engine_ast::Edge *output_edge = can_to_eng_edge_map[*coe];
        output_edge->originalTensor()->setDataFormat(profile->networkOutputDataFormat());

        Dims4 networkDims = output_edge->originalTensor()->getDimensions();
        if ( networkDims.n != (NvS32)profile->multiBatchSize() )
        {
            gLogWarning << "Overriding output multibatch size from " << networkDims.n << " to " << profile->multiBatchSize() << endl;
            networkDims.n = profile->multiBatchSize();
            output_edge->originalTensor()->setDimensions(networkDims);
        }

        output_edge->setBindId(output_edges.size(), IOD_Output);
        if ( eng_graph->debugBinding() )
        {
            gLogInfo << "EngineAST graph level output edge[" << output_edges.size() << "] is " <<                            output_edge->id() << endl;
            gLogInfo << "output bind id: " << output_edge->bindId() << endl;
        }
        output_edges.push_back( output_edge );
    };
	
    //设定整个eng_graph的outputedge列表为output_edges
    if ( output_edges.size() )
    {
        eng_graph->setOutputEdges(output_edges);
    }

    // 打印所有eng_node的name，编号，以及对应的can_node的name
    // 同时打印每个eng_node的所有input output aux类型的edge
    //libnvdla<3> dc-conv-0/n-0/conv1:
	//libnvdla<3> 	in e-0
	//libnvdla<3> 	out e-11
	//libnvdla<3> 	aux e-9
	//libnvdla<3> bias-0/n-1/conv1:
	//libnvdla<3> 	in e-11
	//libnvdla<3> 	out e-1
	//libnvdla<3> 	aux e-10
    if ( eng_graph->debugGraphDump() )
    {
        engine_ast::Graph::NodeSet engineNodes = eng_graph->nodes();
        engine_ast::Graph::NodeSetIterator eni = engineNodes.begin();
        for ( ; eni != engineNodes.end(); ++eni)
        {
            typedef std::vector<Edge*>::const_iterator ESI;
            std::string canNodeName;
            if ((*eni)->canonicalNode() == NULL)  canNodeName = "(No canonical node)";
            else canNodeName = (*eni)->canonicalNode()->name();
            
            gLogInfo << (*eni)->name() << "/" << (*eni)->id() << "/"
                     << canNodeName << ":" << endl;
            for (ESI ii = (*eni)->inputEdges().begin(); ii != (*eni)->inputEdges().end(); ++ii)
                gLogInfo << "\tin " << (*ii)->id() << endl;
            for (ESI ii = (*eni)->outputEdges().begin(); ii != (*eni)->outputEdges().end(); ++ii)
                gLogInfo << "\tout " << (*ii)->id() << endl;
            for (ESI ii = (*eni)->auxEdges().begin(); ii != (*eni)->auxEdges().end(); ++ii)
                gLogInfo << "\taux " << (*ii)->id() << endl;
        }
    }

    //对所有eng_node进行打分排序？？
    eng_graph->ordering()->generate();
    eng_graph->markClean();

    // force N = 1 for all non-Aux tensors represented by non-bindable edges;
    // until we allow contiguous non-bindable tensors for multi-batch
    // Forcing batch size '1' for non-bindable non-aux edge "
    {
        //迭代所有engine_edges
        engine_ast::Graph::EdgeSequence engineEdges = eng_graph->orderedEdges();
        for (engine_ast::Graph::EdgeSequenceIterator eei = engineEdges.begin(); eei !=                            engineEdges.end(); ++eei)
        {
            //非bindable，非auxedge，并且存在originalTensor
            if (!(*eei)->bindable() && !(*eei)->isAuxEdge() && (*eei)->originalTensor())
            {
                //获取originalTensor的dimension
                Dims4 nonBindableTensorDims = (*eei)->originalTensor()->getDimensions();
                if ( eng_graph->debugGraphDump() )
                {
                    if (nonBindableTensorDims.n != 1)
                        gLogInfo << "Forcing batch size '1' for non-bindable non-aux edge " <<                                           (*eei)->id() << endl;
                }
                nonBindableTensorDims.n = 1;
                (*eei)->originalTensor()->setDimensions(nonBindableTensorDims);
            }
        }
    }
    return eng_graph;

fail:
    return NULL;
}
```

整个函数实现了canonical_graph到engine_graph的变换，用LeNet5作为例子，其具体映射关系可以用下图进行表示：

![](https://github.com/zeasa/nvdla-compiler/raw/master/document/imgs/cangraph2enggraph.png)

刚刚代码里提到了一个重要的函数engine_ast::transformCanNode()，从can_node到eng_node的转换工作都在这个函数中完成，这里来看看其代码：

```c++
NvDlaError engine_ast::transformCanNode
(
    engine_ast::Graph* engGraph,
    canonical_ast::Node *canNode,
    engine_ast::Graph::EdgeSequence engSrcEdges,
    engine_ast::Graph::EdgeSequence engSinkEdges,
    engine_ast::Graph::NodeSequence& transformedEngNodes
)
{
    NvDlaError e = NvDlaSuccess;

    switch (canNode->canonicalOpType().v())
    {
        case canonical_ast::CONVOLUTION:
            PROPAGATE_ERROR_FAIL(transformCanConvOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::FULLY_CONNECTED:
            PROPAGATE_ERROR_FAIL(transformCanFCOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::ACTIVATION:
            PROPAGATE_ERROR_FAIL(transformCanActOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::POOLING:
            PROPAGATE_ERROR_FAIL(transformCanPoolingOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::LRN:
            PROPAGATE_ERROR_FAIL(transformCanLRNOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::SCALE:
            PROPAGATE_ERROR_FAIL(transformCanScaleOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::BATCH_NORM:
            PROPAGATE_ERROR_FAIL(transformCanBNOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::SOFTMAX:
            PROPAGATE_ERROR_FAIL(transformCanSoftMaxOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::DECONVOLUTION:
            PROPAGATE_ERROR_FAIL(transformCanDeconvOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::CONCATENATION:
            PROPAGATE_ERROR_FAIL(transformCanConcatOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::ELEMENTWISE:
            PROPAGATE_ERROR_FAIL(transformCanEWOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        case canonical_ast::SPLIT:
            PROPAGATE_ERROR_FAIL(transformCanSplitOp(engGraph, canNode, engSrcEdges, engSinkEdges, transformedEngNodes)); break;
        default:
             ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Unexpected canonical node '%s' of type '%s' ", canNode->id().c_str(), canNode->canonicalOpType().c_str());
    }
fail:
    return e;
}
```

可以看到，他的输入是一个can_node，输出是一个或多个eng_node，之所以可能是多个就是应为刚刚提到的network中的一层操作有可能是分配给多个不同功能的dla引擎共同完成的，例如一个conv操作，其中的bias部分就不是dla的conv引擎的工作，而是分配给了SDP引擎来完成，所以在engine_graph这个层次的图中就要把这种操作表示成两个node。上述函数根据can_node的类型，分别调用了不同的转换函数来完成转换，我们挑其中一个来说明其大致思路。

```c++
//transformCanConvOp完成conv类型的canNode到engNode的转换操作
static NvDlaError transformCanConvOp
(
    engine_ast::Graph* engGraph,
    canonical_ast::Node *canNode,//输入是一个canNode
    engine_ast::Graph::EdgeSequence engSrcEdges,
    engine_ast::Graph::EdgeSequence engSinkEdges,
    engine_ast::Graph::NodeSequence& transformedEngNodes//输出是一个或多个engNodes
)
{
    NvDlaError e = NvDlaSuccess;
    bool isWG = false;
    bool isInputBindable  = false;
    bool isOutputBindable = false;
    canonical_ast::ConvolutionNode* canConvNode        = NULL;
    engine_ast::ConvCoreNode* engConvNode              = NULL;
    engine_ast::SDPNode* adjointSDPNode                = NULL;
    engine_ast::Edge* engSrcEdge                       = NULL;
    engine_ast::Edge* engSinkEdge                      = NULL;
    engine_ast::Edge* convAuxEdge                      = NULL;
    engine_ast::Edge* sdpAuxEdge                       = NULL;
    //获取canNode所在的can_graph的所有inputEdges
    canonical_ast::Graph::EdgeSequence canInputEdges   = canNode->graph()->inputEdges();
    //获取canNode所在的can_graph的所有outputEdges
    canonical_ast::Graph::EdgeSequence canOutputEdges  = canNode->graph()->outputEdges();
	
    //转换操作只支持conv的输入输出edge都是1的类型
    if (engSrcEdges.size() != 1 || engSinkEdges.size() != 1)
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "Don't support Conv operation with input edges (%d) != 1 or " "output edges (%d) != 1", engSrcEdges.size(), engSinkEdges.size());
    }

    engSrcEdge     = engSrcEdges[0];//实际上engSrcEdges[]数组也只有一个元素
    engSinkEdge    = engSinkEdges[0];//实际上engSinkEdge[]数组也只有一个元素
    //canNode转换为canConvNode
    canConvNode    = canonical_ast::NodeFactory::nodeCast<canonical_ast::ConvolutionNode*>(canNode);
    //根据canConvNode构造engConvNode<这条语句后面单独解析>
    engConvNode    = engine_ast::NodeFactory::newConvCoreConvolutionOpNode(canConvNode, engGraph);
    //adjointSDPNode是由engConvNode根据canConvNode创建的，创建完毕直接和engConvNode进行关联
    adjointSDPNode = engConvNode->addSDPJointOpNode(canConvNode);
    //设定adjointSDPNode工作模式，因为SDP引擎功能较多
    adjointSDPNode->params().setConvMode(engConvNode->params().convMode());

    ASSERT( canNode->inputEdges().size() == 1 );
    ASSERT( canNode->outputEdges().size() == 1 );
	
    //判断当前要转换的节点的输入edge是否是整个graph的输入edge
    isInputBindable  = std::find(canInputEdges.begin(), canInputEdges.end(), canNode->inputEdges().at(0)) != canInputEdges.end();
    //判断当前要转换的节点的输出edge是否是整个graph的输出edge
    isOutputBindable = std::find(canOutputEdges.begin(), canOutputEdges.end(), canNode->outputEdges().at(0)) != canOutputEdges.end();
    //判断engConvNode的conv模式是否是WINOGRAD
    isWG = engConvNode->params().convMode() == engine_ast::ConvolutionModeEnum::CONV_WINOGRAD;
	
    //WINOGRAD模式的conv操作不适合作为系统的输入或者输出节点
    if (isWG && (isInputBindable || isOutputBindable))
    {
        gLogWarning << "Can't use WG mode with bindable surfaces. Falling back to CONV_DIRECT for "
                    << engConvNode->name() << endl;
        isWG = false;
        engConvNode->setName("dc-conv-" + engConvNode->name().substr(engConvNode->name().find("wg-conv-") + 8));
        engConvNode->params().setConvMode(engine_ast::ConvolutionModeEnum::CONV_DIRECT);
        adjointSDPNode->params().setConvMode(engine_ast::ConvolutionModeEnum::CONV_DIRECT);
    }
	
    //把engSrcEdge连接到刚刚创建的engConvNode的输入edge侧
    engGraph->appendNodeToEdge(engSrcEdge, ast::EdgeSideEnum::SECOND, engConvNode);
    //把engSinkEdge连接到刚刚创建的adjointSDPNode的输出edge侧
    engGraph->appendNodeToEdge(engSinkEdge, ast::EdgeSideEnum::FIRST, adjointSDPNode);
    
	//为engConvNode创建并关联auxEdge，这个auxEdge用来向conv节点输入weight数据
    PROPAGATE_ERROR_FAIL(engConvNode->nodeAuxEdge(&convAuxEdge));
    //为adjointSDPNode创建并关联auxEdge，这个auxEdge用来向sdp节点输入bias数据
    PROPAGATE_ERROR_FAIL(adjointSDPNode->nodeAuxEdge(&sdpAuxEdge));

    PROPAGATE_ERROR_FAIL(engConvNode->populateEdgePorts());
    transformedEngNodes.push_back(engConvNode);//把engConvNode加入函数返回node列表中

    PROPAGATE_ERROR_FAIL(adjointSDPNode->populateEdgePorts());
    transformedEngNodes.push_back(adjointSDPNode);//把adjointSDPNode加入函数返回node列表中

    if (isWG)//Winograd参数
    {
        PROPAGATE_ERROR_FAIL(engConvNode->determineWinogradParams());
        PROPAGATE_ERROR_FAIL(adjointSDPNode->determineWinogradParams(engConvNode));
    }
fail:
    return e;
}

NvDlaError engine_ast::ConvCoreNode::nodeAuxEdge(engine_ast::Edge **ret_edge)
{
    NvDlaError e = NvDlaSuccess;
    //可以看到conv节点的auxedge，其实也是一种dataEdge，只不过其type=WEIGHT，side=SECOND(输入)
    PROPAGATE_ERROR_FAIL(nodeDataEdge(TensorType::kWEIGHT, ast::EdgeSideEnum::SECOND, ret_edge));
fail:
    return e;
}
NvDlaError engine_ast::Node::populateEdgePorts()
{
    NvDlaError e = NvDlaSuccess;
	//找到当前node的上下游dataedge
    EdgeSequence inputEdges = graph()->upstreamDataEdges(this);
    EdgeSequence outputEdges = graph()->downstreamDataEdges(this);

    //should be min 1 upstream edge;
    //if only 1 upstream edge, it should be the data input
    //if >1 upstream edges, find input and/or aux edges
    if (inputEdges.size() == 0)
        ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "%s has 0 input edges", name().c_str());
    else if (inputEdges.size() == 1)//如果当前node只有一个inputEdge则标记为InputEdge
        markInputEdge(inputEdges[0]);
    else
    {
        //当前node不止一个inputEdge，则根据是否是AuxEdge标记为InputEdge或者AuxEdge
        for (EdgeSequenceIterator iei = inputEdges.begin(); iei != inputEdges.end(); ++iei)
        {
            if ((*iei)->isAuxEdge())
                markAuxEdge(*iei);
            else
                markInputEdge(*iei);
        }
    }

    //* should be exactly only 1 output edge, it should be the data output,
    // * none of the engine nodes is capable of >1 outputs, fail if so since
    // * concat and split nodes are handled separately
    //所有的engnode都只能有一个outputEdge，concat或者split操作单独处理
    if (outputEdges.size() == 0)
        ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "%s has 0 output edges", name().c_str());
    else if (outputEdges.size() == 1)
        markOutputEdge(outputEdges[0]);
    else
        ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "%s has >1 output edges", name().c_str());

    PROPAGATE_ERROR_FAIL( verifyEdgePorts() );
fail:
    return e;
}

//这个函数完成的是从canNode来创建engConvNode的功能
engine_ast::ConvCoreConvolutionOpNode* engine_ast::NodeFactory::newConvCoreConvolutionOpNode
(
    canonical_ast::ConvolutionNode* origCanNode,
    engine_ast::Graph* engGraph
)
{
    typedef typename engine_ast::Node* B;
    typedef typename engine_ast::ConvCoreConvolutionOpNode* DD;

    B b;
    DD dd;
    NvU16 numBatches = engGraph->profile()->multiBatchSize();

    //建立engConv节点
    b = dd = new engine_ast::ConvCoreConvolutionOpNode(origCanNode, numBatches);
    dd->setId(engGraph->nextNodeId());//节点Id=n-0,n-1
    dd->setGraph(engGraph);//node的container指向graph
    //根据canNode的属性填充当前engNode的属性
    dd->captureCanonicalParams();
    engGraph->insertNode(b);//把当前建立的节点加入Graph的node列表中

    // determine op mode for the conv op: DC / WINOGRAD
    WeightTrns::WeightDims weightDims (dd->params().rawWeights().count,
                                       dd->params().weightDims().n,
                                       dd->params().weightDims().c,
                                       dd->params().weightDims().w,
                                       dd->params().weightDims().h,
                                       dd->params().stride().w,
                                       dd->params().stride().h);
    // fixme: disable winograd with group conv since group conv tends to bloat weight size
    // by a factor of 'inputC / auxC' which can be arbitrarily large to fit in CBUFF
    bool canWG          = engGraph->profile()->canWinograd();
    bool isWGPossible   = WeightTrns::isWGPossible(weightDims);
    bool isGroupConv    = dd->params().numGroups() > 1;
    bool isDilation     = dd->params().dilation() != Dims2(1,1);
    bool isInt8         = engGraph->profile()->computePrecision().v() ==
                          surface::SurfacePrecisionEnum::NVDLA_PRECISION_INT8;
    if ( canWG && isWGPossible && !isGroupConv && !isDilation && !isInt8 )
    {
        dd->setName(std::string("wg-conv-") + toString(s_conv_conv_priv.size()));
        dd->params().setConvMode(engine_ast::ConvolutionModeEnum::CONV_WINOGRAD);
    }
    else
    {
        dd->setName(std::string("dc-conv-") + toString(s_conv_conv_priv.size()));
        dd->params().setConvMode(engine_ast::ConvolutionModeEnum::CONV_DIRECT);
    }

    s_conv_conv_priv.insert(std::pair<B, DD>(b, dd));
    return dd;
}
//从canNode拷贝Node的属性到engNode
void engine_ast::ConvCoreConvolutionOpNode::captureCanonicalParams()
{
    params().setHasBiasTerm(canonicalNode()->params().hasBiasTerm() == true ? 1 : 0);
    params().setWeightDims(canonicalNode()->params().weightDims());
    params().setTopLeftPadding(canonicalNode()->params().topLeftPadding());
    params().setBottomRightPadding(canonicalNode()->params().bottomRightPadding());
    params().setPaddingValue(canonicalNode()->params().paddingValue());
    params().setStride(canonicalNode()->params().stride());
    params().setDilation(canonicalNode()->params().dilation());
    params().setRawWeights(canonicalNode()->params().weights());
    params().setDLAWeights(Weights(DataType::FLOAT, NULL, 0));
    params().setNumGroups(canonicalNode()->params().numGroups());
    captureCanonicalWeights();
}
//为engNode建立Weight的tensor和edge
NvDlaError engine_ast::ConvCoreNode::captureCanonicalWeights()
{
    NvDlaError e = NvDlaSuccess;
    Tensor* wt_tensor;
    wt_tensor = graph()->addAuxTensor(graph()->newAuxTensorName(), params().weightDims(), TensorType::kWEIGHT);
    Edge* aux = graph()->addDataEdge((canonical_ast::Edge*)0, 0, this, wt_tensor);
    NVDLA_UNUSED(aux);
    return e;
}
```



### 4.3.6.代码流程分析-EngineAST中间IR变换与优化PASS
1.注册缓存 registerBuffers,分为两个部分，一是注册接口，二是注册buffer
```c++
    PROPAGATE_ERROR_FAIL(graph->registerAllSurfaces());
    PROPAGATE_ERROR_FAIL(graph->registerAllBuffers());
```
首先是注册接口。
```c++
    FOR_EACH(allNodes, NodeSequenceIterator, clearNodeTSDStateMapping);//清除tensorsurfacedescribe与Node的映射关系

    FOR_EACH(allEdges, EdgeSequenceIterator, registerSurface);//注册接口
    FOR_EACH(allEdges, EdgeSequenceIterator, determineSurfaceClients);//注册接口成员
    FOR_EACH(allEdges, EdgeSequenceIterator, determineSurfaceFormat);//注册接口格式
    FOR_EACH(allEdges, EdgeSequenceIterator, determineSurfaceStrides);//注册张量的stride
    FOR_EACH(allEdges, EdgeSequenceIterator, determineSurfaceSize);//注册接口大小
    FOR_EACH(allEdges, EdgeSequenceIterator, determineSurfaceOffsetInBuffer);//注册接口offsetbuffer

    PROPAGATE_ERROR_FAIL( verifyAllSurfaces() );
```
确认接口是否注册正确
```c++
 /* Verify that the producers and consumers of the tsd are
     * the same as the physical upstream and downstream nodes
     */
    PROPAGATE_ERROR_FAIL( verifySurfaceClients() );

    /* Verify that the surface format determined for the tsd are
     * compatible with all the node(s) operating on it.
     */
    PROPAGATE_ERROR_FAIL( verifySurfaceFormat() );

    /* Verify that none of the node(s) changed the dims of any tsd,
     * such that the node(s) on the other end of that tsd couln't
     * operate on it anymore
     */
    PROPAGATE_ERROR_FAIL( verifySurfaceDims() );

    /* Verify that the surface strides determined for the tsd are
     * compatible with all the node(s) operating on it.
     */
    PROPAGATE_ERROR_FAIL( verifySurfaceStrides() );

    /* Verify that the size determined for the tsd are
     * compatible with all the node(s) operating on it.
     */
    PROPAGATE_ERROR_FAIL( verifySurfaceSize() );

    /* Verify that the surface offset determined in the buffer
     * for the tsd is compatible with all the node(s) operating on it.
     */
    PROPAGATE_ERROR_FAIL( verifySurfaceOffsetInBuffer() );

    /* Verify that each tensor has channel scales set and
     * that they are valid
     */
    PROPAGATE_ERROR_FAIL( verifySurfaceTensorScales() );
```
其次是注册buffer
```c++
NvDlaError engine_ast::Graph::registerAllBuffers()
{
    NvDlaError e = NvDlaSuccess;
    EdgeSequence allEdges   = orderedEdges();

    for (EdgeSequenceIterator ei = allEdges.begin(); ei != allEdges.end(); ++ei)
    {
        PROPAGATE_ERROR_FAIL((*ei)->registerBuffer());
    }

    PROPAGATE_ERROR_FAIL( verifyAllBuffers() );

fail:
    return e;
}
```
```c++
NvDlaError engine_ast::Edge::registerBuffer()
{
    NvDlaError e = NvDlaError_Success;
    typedef memory::TensorBufferDesc TBD;

    surface::TensorSurfaceDesc *tsd;
    Graph::NodeUnorderedSet producers;
    Graph::NodeUnorderedSet consumers;
    Graph::NodeUnorderedSet clients;

    TBD* currTBD = NULL;
    TBD* commonTBD = NULL;
    std::map<Node*, TBD*> clientBufferMap;

    tsd = tensorSurfaceDesc();

    if ( !isDataEdge() )
    {
        goto fail;
    }
    else if (!tsd)
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "TSD not yet registered for edge %s", id().c_str());
    }
    else if ( tsd->tensorCategory().v() == memory::TensorCategoryEnum::UNKNOWN_TENSOR )
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Edge %s has 'unknown' tensor category",
                             tsd->id().c_str());
    }

    producers = tsd->producers();
    consumers = tsd->consumers();
    clients.insert(producers.begin(), producers.end());
    clients.insert(consumers.begin(), consumers.end());

    commonTBD = tsd->tensorBufferDesc();
    if ( !commonTBD )//如果没有设置缓存
    {
        Graph::NodeUnorderedSetIterator cli;

        for (cli = clients.begin(); cli != clients.end(); ++cli)
        {
            if ((*cli)->isSoftwareNode())
            {
                commonTBD = (*cli)->suggestBuffer(tsd);
                break;
            }
        }

        // Step-1: If there's a software client, prefer its suggested TBD
        //         don't bother querying the TBDs from non-software clients
        if (commonTBD)
        {
            tsd->setTensorBufferDesc(commonTBD);
        }
        // Step-2: If there's no software client, assert that all clients suggested 1 common TBD
        else
        {
            for (cli = clients.begin(); cli != clients.end(); ++cli)
            {
                currTBD = (*cli)->suggestBuffer(tsd);
                if (cli == clients.begin())
                {
                    commonTBD = currTBD;
                    tsd->setTensorBufferDesc(commonTBD);
                }
                else
                {
                    ASSERT(currTBD == commonTBD);
                }
            }
        }
    }

    PROPAGATE_ERROR_FAIL( commonTBD->addSurface(tsd) );//添加接口
    if ( graph()->debugBuffers() )//这里输出日志信息每一个tsd里包含着一个tsb
    {
        gLogInfo << commonTBD->id() << " for " << tsd->id() << " for " << id() << " with " << tsd->surfaceFormat().c_str() << endl;
    }

fail:
    return e;
}
```
2.preProcessAuxData 预量化 针对的是第一层convop,以ConvCoreNode为例。
```c++
NvDlaError engine_ast::ConvCoreNode::preProcessAuxData()
{
    NvDlaError e = NvDlaSuccess;

    bool isIMGConv      = false;
    Edge* dataInputEdge = NULL;

    PROPAGATE_ERROR_FAIL( verifyEdgePorts() );

    dataInputEdge = inputEdges()[0];
    // 枚举类型：IMG、FEATURE_DATA、WEIGHT、BIAS_DATA、BATCH_NORM_DATA、SCALE_DATA
    isIMGConv     = dataInputEdge->tensorSurfaceDesc()->surfaceFormat().category() == surface::SurfaceCategoryEnum::IMG;

    // dilation is not possible with IMG convolution
    if (isIMGConv && (params().dilation().h > 1 || params().dilation().w > 1))
    {
        PROPAGATE_ERROR_FAIL(NvDlaError_NotSupported, "Dilation with image convolution is not supported\n");
    }

    // quantize weights if img Conv, since int8 weights have to undergo
    // pre and/or post Chnl Ext for IMG Conv
    // 如果数据是输入的第一层卷积，就进行量化
    if (isIMGConv)
    {
        PROPAGATE_ERROR_FAIL( quantizeAuxData() );
    }

    // pre-process weights for grouped DC/WG/Deconv convolutions
    if (params().numGroups() != 1)
    {
        PROPAGATE_ERROR_FAIL( squashWeightGroups() );

    }

    // pre-process weights for IMG convolution
    if (isIMGConv)
    {
           PROPAGATE_ERROR_FAIL( processWtsForIMG() );
    }


fail:
    return e;
}
```
判断如果输入edge数据格式为IMG那么进行量化。
```c++
NvDlaError engine_ast::ConvCoreNode::quantizeAuxData()
{
    NvDlaError e = NvDlaSuccess;

    Edge* auxEdge = NULL;
    surface::SurfacePrecision computePrecision = graph()->profile()->computePrecision();
    Weights origWtsBlob = params().rawWeights();
    Weights quantizedWtsBlob;
    NvS8* quantizedWts = NULL;
    std::vector<NvF32> filterScales;

    NvU32 G = params().numGroups();
    NvU32 K = auxSurfaces().back()->dimensions().n / G;
    NvU32 C = auxSurfaces().back()->dimensions().c / G;
    NvU32 RS = auxSurfaces().back()->dimensions().h * auxSurfaces().back()->dimensions().w; // per-group values
    NvU32 kStride = C * RS;
    NvU32 cStride = RS;


    PROPAGATE_ERROR_FAIL( verifyEdgePorts() );

    auxEdge = auxEdges().at(0);

    // quantize weights iff computing in low precision
    if (computePrecision.v() != surface::SurfacePrecisionEnum::NVDLA_PRECISION_INT8)
    {
        // nop
        goto fail;
    }
    // if caffe weights are already int8, then there's no need for quantization
    else if (params().rawWeights().type == nvdla::DataType::INT8)
    {
        // nop
        goto fail;
    }
    // if surface precision for aux edge is not int8, then there's no need for quantization
    else if (auxEdge->tensorSurfaceDesc()->surfaceFormat().f().precision().v() !=
             surface::SurfacePrecisionEnum::NVDLA_PRECISION_INT8)
    {
        goto fail;
    }
    // if already quantized, return
    else if ( params().filterScales().size() )
    {
        // might be already quantized and rearranged with pre/post Chnl Ext for IMG Conv,
        // no more quantization needed
        goto fail;
    }

    // not yet support weight quantization for group convolutions
    if (params().numGroups() != 1)
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "Don't support weight quantization for group convolutions yet for %s\n",
                                name().c_str());
    }
    // 为量化之后的 Tensor 数据开辟内存
    quantizedWts = reinterpret_cast<NvS8*>(std::malloc(origWtsBlob.count * sizeof(NvS8)));
    //量化模式如果是PER_KERNEL
    if (graph()->profile()->quantizationMode() == nvdla::QuantizationMode::PER_KERNEL)
    {
        PRECISION_SWITCH(origWtsBlob.type.v(), computePrecision.v(), filterScales, WeightTrns::perKernelQuantizeWts,
                                                                                   origWtsBlob,
                                                                                   G, K, C, RS, kStride, cStride,
                                                                                   quantizedWts);
        if ( filterScales.size() )
        {
            params().setFilterScales(filterScales);
        }
        else
        {
            ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "Something went wrong with wt quantization for %s\n",
                                    name().c_str());
        }
    }//如果量化模式是perfilter
    else if (graph()->profile()->quantizationMode() == nvdla::QuantizationMode::PER_FILTER)
    {
        PRECISION_SWITCH(origWtsBlob.type.v(), computePrecision.v(), filterScales, WeightTrns::perFilterQuantizeWts,
                                                                                   origWtsBlob,
                                                                                   G, K, C, RS, kStride, cStride,
                                                                                   quantizedWts);
        if ( filterScales.size() )
        {
            params().setFilterScales(filterScales);
        }
        else
        {
            ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "Something went wrong with wt quantization for %s\n",
                                    name().c_str());
        }
    }
    else
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "Quantization mode %s not supported",
                                graph()->profile()->quantizationMode().c_str());
    }

    quantizedWtsBlob.type   = DataType::INT8;
    quantizedWtsBlob.values = quantizedWts;
    quantizedWtsBlob.count  = origWtsBlob.count;

    params().setRawWeights(quantizedWtsBlob);

fail:
    return e;
}
```
这里以INT8 模式 PerKernel为例（不同channel的scale值相同）,量化原理是遍历tensor的权重值得到最大值max，如果max低于阈值那么，scale取一，如果max不低于阈值，scale取max/127。然后每个权重*invscale。量化后最好得到量化参数表filterscales。
```c++
template <typename MP, typename CP>
  static std::vector<NvF32> perKernelQuantizeWts
      (
          Weights highPrecWts,
          NvS32 G, NvS32 K, NvS32 C, NvS32 RS, NvS32 kStride, NvS32 cStride,
          NvS8* quantizedWts
      )
  {
    std::vector<NvF32> filterScales;
    NvF32 max = std::numeric_limits<NvF32>::lowest(); // 先把 max 初始化为 FLoat 32 的最小值
    const MP* origWts = reinterpret_cast<const MP*>(const_cast<void*>(highPrecWts.values));
    // 获取所有Tensor的最大值
    for (NvS32 g = 0; g < G; g++)
    {
      NvS32 gOffset = g * K * C * RS;
      for (NvS32 k = 0; k < K; k++)
      {
        for (NvS32 c = 0; c < C; c++)
        {
          for (NvS32 rs = 0; rs < RS; rs++)
            // max = std::max(max, std::abs(origWts[gOffset + k * kStride + c * cStride + rs] * inScale));
            max = std::max<NvF32>(max, std::fabs(origWts[gOffset + k * kStride + c * cStride + rs]));
        }
      }
    }

    NvF32 scale = (std::fabs(max) < 1e-6)? 1 : max / 127, invScale = 1 / scale;

    // 开始量化
    for (NvS32 g = 0; g < G; g++)
    {
      NvS32 gOffset = g * K * C * RS;
      for (NvS32 k = 0; k < K; k++)
      {
        for (NvS32 c = 0; c < C; c++)
        {
          for (NvS32 rs = 0; rs < RS; rs++)
          {
            NvS32 index = gOffset + k * kStride + c * cStride + rs;
            // quantizedWts[index] = int8_t(std::floor(origWts[index] * inScale * invScale + 0.5f));

            // quantizedWts[index] = static_cast<NvS8>(std::floor(origWts[index] * invScale + 0.5f));
            NvS32 int32Weight = static_cast<NvS32>(std::floor(origWts[index] * invScale + 0.5f));
            quantizedWts[index] = static_cast<NvS8>(std::max(std::min(int32Weight, static_cast<NvS32>(std::numeric_limits<NvS8>::max())),
                                                             static_cast<NvS32>(std::numeric_limits<NvS8>::lowest())));
          }
        }
        filterScales.push_back(scale);
      }
    }
    return filterScales;
  }

  //! Quantize weights per-filter (1 scaling factor for each CRS blob)
  template <typename MP, typename CP>
  static std::vector<NvF32> perFilterQuantizeWts
      (
          Weights highPrecWts,
          NvS32 G, NvS32 K, NvS32 C, NvS32 RS, NvS32 kStride, NvS32 cStride,
          NvS8* quantizedWts
      )
  {
    std::vector<NvF32> filterScales;
    const MP* origWts = reinterpret_cast<const MP*>(const_cast<void*>(highPrecWts.values));

    for (NvS32 g = 0; g < G; g++)
    {
      NvS32 gOffset = g * K * C * RS;
      for (NvS32 k = 0; k < K; k++)
      {
        NvF32 max = std::numeric_limits<NvF32>::lowest();
        for (NvS32 c = 0; c < C; c++)
        {
          for (NvS32 rs = 0; rs < RS; rs++)
            // max = std::max(max, std::abs(origWts[gOffset + k * kStride + c * cStride + rs] * inScale));
            max = std::max<NvF32>(max, std::fabs(origWts[gOffset + k * kStride + c * cStride + rs]));
        }

        NvF32 scale = (std::fabs(max) < 1e-6)? 1 : max / 127, invScale = 1 / scale;


        for (NvS32 c = 0; c < C; c++)
        {
          for (NvS32 rs = 0; rs < RS; rs++)
          {
            NvS32 index = gOffset + k * kStride + c * cStride + rs;
            // quantizedWts[index] = int8_t(std::floor(origWts[index] * inScale * invScale + 0.5f));

            // quantizedWts[index] = static_cast<NvS8>(std::floor(origWts[index] * invScale + 0.5f));
            NvS32 int32Weight = static_cast<NvS32>(std::floor(origWts[index] * invScale + 0.5f));
            quantizedWts[index] = static_cast<NvS8>(std::max(std::min(int32Weight, static_cast<NvS32>(std::numeric_limits<NvS8>::max())),
                                                             static_cast<NvS32>(std::numeric_limits<NvS8>::lowest())));
          }
        }

        filterScales.push_back(scale);
      }
    }
    return filterScales;
  }

```
3.mergeActionOperations 如何激活值算子 这里以relu为例
```c++
NvDlaError engine_ast::Graph::mergeActivationOperations()
{
    NvDlaError e = NvDlaSuccess;
    NodeSequence allNodes = orderedNodes();
    NodeSequenceIterator ni = allNodes.begin();
    NodeSequenceIterator startNodeIter = ni;
    bool maxOptimized = false;
    Node* currNode   = NULL;//当前算子
    Node* prevNode   = NULL;//上一算子
    Node* removeNode = NULL;
    //如果profile中canSDOMergeMathOps和canSDPBustNOPs为1，则跳出这个pass
    if ( !profile()->canSDPMergeMathOps() && !profile()->canSDPBustNOPs() )
    {
        // nothing to do
        goto fail;
    }

    PROPAGATE_ERROR_FAIL( mergeUnitScaleOperations() );

    do
    {
        for (ni = startNodeIter; ni != allNodes.end(); ++ni)
        {
            /* Currently only mathematical ops executable on CONV/SDP can be combined;
             * skip the rest
             */
            if ((*ni)->engineType().v() != EngineTypeEnum::SDP &&
                (*ni)->engineType().v() != EngineTypeEnum::CONVOLUTION)
            {
                continue;
            }

            NodeSequence sinkNodes = downstreamDataNodes((*ni));
            /* Attempt to combine only those sdp nodes which are 1:1 connected and
             * not part of a multi-way junction
             */
            if ( sinkNodes.size() != 1 || upstreamDataNodes(sinkNodes[0]).size() != 1 ||
                 sinkNodes[0]->engineType().v() != EngineTypeEnum::SDP )
            {
                continue;
            }

            currNode   = *ni;
            prevNode   = ni != allNodes.begin() ? *(ni - 1) : *ni;
            SDPNode* nextSDP = NodeFactory::nodeCast<SDPNode*>(sinkNodes[0]);

            if ( debugMathOptz() )
            {
                gLogInfo << std::endl;
                gLogInfo << "Try Merging: " << currNode->name() << " & " << nextSDP->name() << std::endl;
            }

            removeNode = currNode->mergeWithSDPOp(nextSDP);

            if ( debugMathOptz() )
            {
                if (removeNode)
                    gLogInfo << "Merging: Sucess" << std::endl;
                else
                    gLogInfo << "Merging: Not Feasible" << std::endl;
            }

            if (removeNode)
            {
                IODirection iod;
                NodeSequence gNodes = orderedNodes();

                /* Before removing, delegate operation mode to the next op iff it exists;
                 * don't bother if it is already removed from graph
                 */
                if ((removeNode == currNode) && (std::find(gNodes.begin(), gNodes.end(), nextSDP) != gNodes.end()))
                {
                    SDPNode* removeSDP = NULL;
                    ASSERT(removeNode->engineType().v() == EngineTypeEnum::SDP);
                    removeSDP = NodeFactory::nodeCast<SDPNode*>(removeNode);
                    nextSDP->params().setConvMode(removeSDP->params().convMode());
                    nextSDP->params().setWinogradParams(removeSDP->params().winogradParams());
                    nextSDP->params().setNumGroups(removeSDP->params().numGroups());
                }
                else if (removeNode == nextSDP)
                {
                    NodeSequence removeSDPSinkNodes = downstreamDataNodes(nextSDP);
                    NodeWithSameEngineType match_next_sdp(EngineTypeEnum::SDP);
                    NodeSequenceIterator dni = std::find_if(removeSDPSinkNodes.begin(),
                                                            removeSDPSinkNodes.end(),
                                                            match_next_sdp);
                    if (dni != removeSDPSinkNodes.end())
                    {
                        SDPNode* removeSDP = NodeFactory::nodeCast<SDPNode*>(removeNode);
                        SDPNode* removeSDPSinkSDP = NodeFactory::nodeCast<SDPNode*>(*dni);
                        removeSDPSinkSDP->params().setConvMode(removeSDP->params().convMode());
                        removeSDPSinkSDP->params().setWinogradParams(removeSDP->params().winogradParams());
                        removeSDPSinkSDP->params().setNumGroups(removeSDP->params().numGroups());
                    }
                }

                /*
                 * If collapsing an SDP node into Conv, detach the SDP from its output side
                 * and retain the stream tensor from Conv
                 * If collapsing an SDP node into another SDP, detach the collapsing SDP from
                 * the side that connects to the prevailing SDP
                 */
                if (currNode->engineType().v() == EngineTypeEnum::CONVOLUTION)
                {
                    iod = IODirectionEnum::OUTPUT;
                }
                else
                {
                    iod = (removeNode == currNode) ? IODirectionEnum::OUTPUT : IODirectionEnum::INPUT;
                }

                PROPAGATE_ERROR_FAIL( removeNodeFromAST(removeNode, iod) );
                break;
            }
        }

        // if the last pass through all nodes didn't change the AST anymore,
        // that means all optimizations are applied; no more scope left
        if ( ni == allNodes.end() )
        {
            maxOptimized = true;
        }
        else
        {
            // rinse and repeat on newly ordered nodes;
            // starting from the node prior to the recently operated one
            allNodes = orderedNodes();
            startNodeIter = std::find(allNodes.begin(), allNodes.end(), prevNode);
            if (startNodeIter == allNodes.end())
            {
                startNodeIter = allNodes.begin();   // just in case
            }
            PROPAGATE_ERROR_FAIL(refreshGraphState());
        }
    } while(!maxOptimized);

    // check dirty and re-determine graph order
    checkDirty();
    PROPAGATE_ERROR_FAIL(refreshGraphState());

fail:
    return e;
}
/*-----------------------Merge Unit Scale Operations-------------------------*/
/*
 * Unit scale operations are introduced for int8 scaling when there is no
 * adjacent SDP operation to perform compression to int8 space. But these
 * unit scale operations can be merged if another adjacent SDP is available.
 * Remove such unit scale operations before start merging other SDP ops.
 *这个操作在融合其它SDP算子之前
 */
NvDlaError engine_ast::Graph::mergeUnitScaleOperations()
{
    NvDlaError e = NvDlaSuccess;
    NodeSequence allNodes = orderedNodes();
    NodeSequenceIterator ni = allNodes.begin();
    NodeSequenceIterator startNodeIter = ni;
    bool maxOptimized = false;
    Node* currNode   = NULL;
    Node* prevNode   = NULL;
    Node* removeNode = NULL;

    do
    {   // iterate all Nodes for engine abstract syntax tree
        for (ni = startNodeIter; ni != allNodes.end(); ++ni)
        {
            // The Node type must be SDP
            if ((*ni)->engineType().v() != EngineTypeEnum::SDP)//如果该node不是SDP跳出本次循环
            {
                continue;
            }

            NodeSequence sinkNodes = downstreamDataNodes((*ni));
            /* Attempt to combine only those sdp nodes which are 1:1 connected and
             * not part of a multi-way junction
             */
            if ( sinkNodes.size() != 1 || upstreamDataNodes(sinkNodes[0]).size() != 1 ||
                 sinkNodes[0]->engineType().v() != EngineTypeEnum::SDP )
            {
                continue;
            }

            currNode   = *ni;
            prevNode   = ni != allNodes.begin() ? *(ni - 1) : *ni;//如果不是第一个节点指针指向上一个单位
            SDPNode* currSDP = NodeFactory::nodeCast<SDPNode*>(currNode);
            SDPNode* nextSDP = NodeFactory::nodeCast<SDPNode*>(sinkNodes[0]);
            if ( nextSDP->engineOpType().v() != EngineOpTypeEnum::SDP_SCALE )
            {
                continue;
            }

            if ( !nextSDP->isUnitScale() )
            {
                continue;
            }

            if ( debugMathOptz() )
            {
                gLogInfo << std::endl;
                gLogInfo << "Try Merging: " << currNode->name() << " & " << nextSDP->name() << std::endl;
            }

            removeNode = currSDP->mergeUnitScaleOp(nextSDP);

            if ( debugMathOptz() )
            {
                if (removeNode)
                    gLogInfo << "Merging: Sucess" << std::endl;
                else
                    gLogInfo << "Merging: Not Feasible" << std::endl;
            }

            if ( removeNode )
            {
                IODirection iod = IODirectionEnum::INPUT;

                PROPAGATE_ERROR_FAIL( removeNodeFromAST(removeNode, iod) );
                break;
            }
        }

        // if the last pass through all nodes didn't change the AST anymore,
        // that means all optimizations are applied; no more scope left
        if ( ni == allNodes.end() )
        {
            maxOptimized = true;
        }
        else
        {
            // rinse and repeat on newly ordered nodes;
            // starting from the node prior to the recently operated one
            allNodes = orderedNodes();
            startNodeIter = std::find(allNodes.begin(), allNodes.end(), prevNode);
            if (startNodeIter == allNodes.end())
            {
                startNodeIter = allNodes.begin();   // just in case
            }
            PROPAGATE_ERROR_FAIL(refreshGraphState());
        }
    } while(!maxOptimized);


     // check dirty and re-determine graph order
    checkDirty();
    PROPAGATE_ERROR_FAIL(refreshGraphState());

fail:
    return e;
}
```
以ConvcoreNode为例,可以和scaleop和batchnormop尝试融合
```c++
engine_ast::Node* engine_ast::ConvCoreNode::mergeWithSDPOp(SDPNode* nextSDP)
{
    Node* removableNode = NULL;

    if (nextSDP->engineOpType().v() == EngineOpTypeEnum::SDP_SCALE)
    {
        removableNode = tryToMergeWithScaleOp(nextSDP);
    }
    else if (nextSDP->engineOpType().v() == EngineOpTypeEnum::SDP_BATCH_NORM)
    {
        removableNode = tryToMergeWithBatchNormOp(nextSDP);
    }

    return removableNode;
}
//以conv融合scale参数为题。主要是融合weight值
engine_ast::Node* engine_ast::ConvCoreNode::tryToMergeWithScaleOp(SDPNode* SDPSclOp)
{
    Node* removableNode = NULL;
    SDPScaleOpNode* scaleOp = NodeFactory::nodeCast<SDPScaleOpNode*>(SDPSclOp);
    Weights rawKrnlWts = params().rawWeights();
    Weights rawSclData = scaleOp->params().rawScaleData();
    Dims4 krnlWtDims   = params().weightDims();
    Dims4 sclDims      = scaleOp->params().scaleDims();
    SDPMode sclMode    = scaleOp->params().x1Params().mode();
    Weights combinedWtsAndScaleData;
    WeightTrns wtTrns;

    nvdla::DataType modelPrec             = rawKrnlWts.type == rawSclData.type ?
                                            rawKrnlWts.type :
                                            nvdla::DataType::UNKNOWN;
    surface::SurfacePrecision computePrec = graph()->profile()->computePrecision();

    NodeSequence scaleOpDownNodes;
    NodeSequenceIterator dni;
    NodeWithSameEngineType match_eng_type(EngineTypeEnum::SDP);

    if (!graph()->profile()->canSDPMergeMathOps())
    {
        goto fail;
    }

    // if there's no more SDP operations following the Scale Op, avoid the fusion since
    // the Conv Op will need an SDP write out proxy
    scaleOpDownNodes = graph()->downstreamDataNodes(scaleOp);
    dni = std::find_if(scaleOpDownNodes.begin(), scaleOpDownNodes.end(), match_eng_type);
    if (dni == scaleOpDownNodes.end())
    {
        goto fail;
    }
    // if there's a ReLU op after the scale, don't allow the conv+scale fusion since
    // the scale is a proxy node to perform the int8 rescaling before the relu op
    else if (graph()->profile()->computePrecision() == surface::SurfacePrecisionEnum::NVDLA_PRECISION_INT8 &&
             scaleOpDownNodes.size() &&
             scaleOpDownNodes.at(0)->engineOpType() == engine_ast::EngineOpTypeEnum::SDP_ACTIVATION)
    {
        goto fail;
    }
    // if there's a ELTwise op after the scale, don't allow the conv+scale fusion since
    // the scale is a proxy node to perform the int8 rescaling before the EW op. since
    // the thread with which EW x2 fusion might happen is unknown, avoid the conv+scale fusion on all threads
    else if (graph()->profile()->computePrecision() == surface::SurfacePrecisionEnum::NVDLA_PRECISION_INT8 &&
             scaleOpDownNodes.size() &&
             scaleOpDownNodes.at(0)->engineOpType() == engine_ast::EngineOpTypeEnum::SDP_ELEMENTWISE)
    {
        goto fail;
    }

    // xxx: skip if the dla weights are already arranged. plugging scale factors will be difficult now
    if ( params().DLAWeights().values != NULL )
    {
        goto fail;
    }

    PRECISION_SWITCH(modelPrec.v(), computePrec.v(), combinedWtsAndScaleData,
                                                     wtTrns.combineKernelWeightsAndScaleData,
                                                     sclMode,
                                                     krnlWtDims,
                                                     sclDims,
                                                     rawKrnlWts,
                                                     rawSclData);
    if (combinedWtsAndScaleData.values == NULL)
    {
        if ( debugFactorization() )
        {
            gLogWarning << "Can't successfully combine Kernel weights and Scale factors of "
                        << name() << " and " << scaleOp->name() << endl;
        }
        goto fail;
    }

    params().setRawWeights(combinedWtsAndScaleData);
    removableNode = scaleOp;

fail:
    return removableNode;
}
```
移除节点的具体方法如下：
```c++
NvDlaError engine_ast::Graph::removeNodeFromAST(Node* killNode, IODirection iod)
{
    NvDlaError e = NvDlaSuccess;

    NodeSequence ioSideNodes;
    EdgeSequence ioSideEdges;
    EdgeSequence oppSideEdges;
    Edge* killNodeAuxEdge = NULL;

    if (iod.v() == IODirectionEnum::UNKNOWN)
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Can't remove node unless the "
                "I/O direction of edges to trim is specified: %s", iod.c_str());
    }

    ioSideNodes  = iod.v() == IODirectionEnum::INPUT ? upstreamNodes(killNode) : downstreamNodes(killNode);
    ioSideEdges  = iod.v() == IODirectionEnum::INPUT ? upstreamEdges(killNode) : downstreamEdges(killNode);
    oppSideEdges = iod.v() == IODirectionEnum::INPUT ? downstreamEdges(killNode) : upstreamEdges(killNode);

    killNode->nodeAuxEdge(&killNodeAuxEdge);

    /* Transfer that set of edge(s) of the node_to_be_removed which are going to stay in the graph -
     * to the node(s) on the opposite side
     */
    for (EdgeSequenceIterator oppsei = oppSideEdges.begin(); oppsei != oppSideEdges.end(); ++oppsei)
    {
        if ((*oppsei)->isAuxEdge())
        {
            continue;
        }

        for (NodeSequenceIterator iosni = ioSideNodes.begin(); iosni != ioSideNodes.end(); ++iosni)
        {
            if (iod.v() == IODirectionEnum::INPUT)
            {
                replaceEdgeNodes(*oppsei, ast::EdgeSideEnum::FIRST, killNode, *iosni);
            }
            else
            {
                replaceEdgeNodes(*oppsei, ast::EdgeSideEnum::SECOND, killNode, *iosni);
            }
        }
    }

    /* Detach and delete the specified I/O side edge(s) from the node_to_be_removed and the
     * node(s) on the other side of those edge(s)
     */
    for (EdgeSequenceIterator iosei = ioSideEdges.begin(); iosei != ioSideEdges.end(); ++iosei)
    {
        if ((*iosei)->isAuxEdge())
        {
            continue;
        }

        for (NodeSequenceIterator iosni = ioSideNodes.begin(); iosni != ioSideNodes.end(); ++iosni)
        {
            if (iod.v() == IODirectionEnum::INPUT)
            {
                removeEdgeFromNode(*iosei, ast::EdgeSideEnum::FIRST, *iosni);
                removeNodeFromEdge(*iosei, ast::EdgeSideEnum::FIRST, *iosni);
            }
            else
            {
                removeEdgeFromNode(*iosei, ast::EdgeSideEnum::SECOND, *iosni);
                removeNodeFromEdge(*iosei, ast::EdgeSideEnum::SECOND, *iosni);
            }
        }

        if (iod.v() == IODirectionEnum::INPUT)
        {
            removeEdgeFromNode(*iosei, ast::EdgeSideEnum::SECOND, killNode);
            removeNodeFromEdge(*iosei, ast::EdgeSideEnum::SECOND, killNode);
        }
        else
        {
            removeEdgeFromNode(*iosei, ast::EdgeSideEnum::FIRST, killNode);
            removeNodeFromEdge(*iosei, ast::EdgeSideEnum::FIRST, killNode);
        }

        resourceMgr()->unregTensorSurfaceDesc((*iosei)->tensorSurfaceDesc());
        resourceMgr()->unregTensorBufferDesc((*iosei)->tensorBufferDesc());
        removeEdge(*iosei);
    }

    /* Repopulate the edge ports of the affected node(s) after this edge upheaval */
    for (NodeSequenceIterator iosni = ioSideNodes.begin(); iosni != ioSideNodes.end(); ++iosni)
    {
        PROPAGATE_ERROR_FAIL((*iosni)->repopulateEdgePorts());
    }

    /* Detach and delete the aux edge (if any) of the node_to_be_removed */
    if (killNodeAuxEdge)
    {
        removeEdgeFromNode(killNodeAuxEdge, ast::EdgeSideEnum::SECOND, killNode);
        removeNodeFromEdge(killNodeAuxEdge, ast::EdgeSideEnum::SECOND, killNode);
        resourceMgr()->unregTensorSurfaceDesc(killNodeAuxEdge->tensorSurfaceDesc());
        resourceMgr()->unregTensorBufferDesc(killNodeAuxEdge->tensorBufferDesc());
        removeEdge(killNodeAuxEdge);
        delete killNodeAuxEdge;
    }

    /* Finally remove the node */
    removeNode(killNode);
    delete killNode;
    killNode = NULL;

fail:
    return e;
}
```
4.updateScalingFactors这里主要是针对Elethwise算子的，列举三种不同的情况更新每一次的inputscale。
```c++
NvDlaError engine_ast::Graph::updateScalingFactors()
{
    NvDlaError e = NvDlaSuccess;
    NodeSequence allNodes = orderedNodes();

    if (profile()->computePrecision().v() != surface::SurfacePrecisionEnum::NVDLA_PRECISION_INT8)
    {
        // nop
        goto fail;
    }

    if ( profile()->tensorScalingMode().v() != nvdla::TensorScalingMode::PER_TENSOR )
    {
        // don't support any other scaling mode than PER_TENSOR
        ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "Don't support tensor scaling mode: %s\n",
                                profile()->tensorScalingMode().c_str());
    }

    for (NodeSequence::const_iterator ni = allNodes.begin(); ni != allNodes.end(); ++ni)
    {
        engine_ast::Node* currNode = *ni;

        EngineOpType eng_op_type = currNode->engineOpType();

        EdgeSequence inputEdges;
        EdgeSequence siblingEdges0;
        EdgeSequence siblingEdges1;

        engine_ast::Edge* inputEdge0 = NULL;
        engine_ast::Edge* inputEdge1 = NULL;
        engine_ast::Edge* updateEdge = NULL;

        std::vector<NvF32> inputTensorScales0;
        std::vector<NvF32> inputTensorScales1;
        std::vector<NvF32> updateTensorScales;

        if (eng_op_type.v() != EngineOpTypeEnum::SDP_ELEMENTWISE)
        {
            continue;
        }

        inputEdges = upstreamDataEdges(currNode);

        /* element wise op should have exactly two input edges. */
        if (inputEdges.size() != 2)
        {
            ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "Elt wise op has input edges (%d) != 2 ", inputEdges.size());
        }

        inputEdge0 = inputEdges.at(0);
        inputTensorScales0 = inputEdge0->originalTensor()->getChannelScales();

        inputEdge1 = inputEdges.at(1);
        inputTensorScales1 = inputEdge1->originalTensor()->getChannelScales();

        ASSERT (inputTensorScales0.size() == inputTensorScales1.size())
        if (inputTensorScales0.at(0) == inputTensorScales1.at(0))
        {
            // Incoming scale values are same, no need for update.
            continue;
        }

        siblingEdges0 = siblingDataEdges(inputEdge0);
        siblingEdges1 = siblingDataEdges(inputEdge1);

        /**
         * Elementwise fusion has 3 possible cases
         * 1. Both input nodes to elementwise layer has single output edges
         * 2. One input node has multiple output edges while another has single output edge
         * 3. Both input nodes to elementwise layer has multiple output edges
         *
         * #1, any of the input nodes can be rescaled using scaling factor of another
         *     node. it requires selecting correct scaling factor to use.
         * #2, general policy is to rescale node with single output edge as rescaling
         *     node with multiple edges will cause incorrect input to another node
         * #3, in such case, we need to select scaling factor from two input nodes
         *     and use new SDP scaling node to rescaling
         *
         * Current implementation support #1 and #2, but does not support scaling factor
         * selection for #1.
         */

        if (siblingEdges0.size() == 0 && siblingEdges1.size() == 0)
        {
            /* case 1 */
            updateEdge = inputEdge0;
            updateTensorScales = inputTensorScales1;
        }
        else if (siblingEdges0.size() == 0)
        {
            /** case 2:
             *   when no src node corresponding to first input edge exists (or)
             *      when src node corresponding to first input edge exists, having only
             *      one output edge = first input edge
             *   In other words, no siblings to first input edge
             *   Handled in similar way as that of case 1
             **/
            updateEdge = inputEdge0;
            updateTensorScales = inputTensorScales1;
        }
        else if (siblingEdges1.size() == 0)
        {
            /** case 2:
             *   when no src node corresponding to second input edge exists (or)
             *      when src node corresponding to second input edge exists, having only
             *      one output edge = second input edge
             *   In other words, no siblings to second input edge
             *   Handled in similar way as that of case 1
             **/
            updateEdge = inputEdge1;
            updateTensorScales = inputTensorScales0;
        }
        else
        {
            /* TODO: to handle case 3: when both input nodes have multiple outputs */
            ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported,
                                "Both input nodes having multiple output edges is not supported yet!");
        }
        updateEdge->originalTensor()->setChannelScales(updateTensorScales);

    }

    // check dirty and re-determine graph order
    checkDirty();
    PROPAGATE_ERROR_FAIL(refreshGraphState());

fail:
    return e;
}
```
5.quantizeAuxData 这里量化包括非第一层权重fp32->int8，偏置fp32->int16
因为权重的量化上文分析过了，这里主要给出了量化Bias的具体方法，函数在BiasOp.cpp中
```c++
NvDlaError engine_ast::SDPBiasOpNode::scaleBiasToInt16
(
    ConvCoreNode* fusedConv,
    std::vector<NvF32>& filterScales,
    std::vector<NvF32>& inTensorScales
)
{
    NvDlaError e = NvDlaSuccess;

    NvS32 maxBias;
    NvS32 numBits;
    NvU32 biasShift;
    std::vector< NvS32 > rescaledBias32;

    NvF32 perTensorInTensorScl = inTensorScales.at(0);

    bool isPerKernelQtz  = graph()->profile()->quantizationMode() == nvdla::QuantizationMode::PER_KERNEL;

    NvF32 scaledFP32Bias = 0.0f;
    NvS16 int16Bias      = 0;
    Weights origBiasBlob = params().rawBiasData();
    Weights int16BiasBlob;
    NvS16* pInt16Bias = (NvS16*)std::malloc(origBiasBlob.count * sizeof(NvS16));
    NvU32 numBiasData = origBiasBlob.count;

    if (fusedConv)
    {
        NvU32 numFilters = filterScales.size();
        ASSERT ( filterScales.size() == (size_t)fusedConv->outputEdges().at(0)->tensorSurfaceDesc()->dimensions().c );
        for (NvU32 ff = 0; ff < numFilters; ++ff)
        {
            if ( isPerKernelQtz && (filterScales[0] != filterScales[ff]) )
            {
                ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "Filter scales should be same for %s when PER_KERNEL "
                                    "quantization is ON", fusedConv->name().c_str());
            }
        }

        ASSERT ( inTensorScales.size() == (size_t)fusedConv->inputEdges().at(0)->tensorSurfaceDesc()->dimensions().c );
        for (NvF32 its = 1; its < inTensorScales.size(); ++its)
        {
            if ( perTensorInTensorScl != inTensorScales[its] )
            {
                ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "Channel scales should be same for input of %s when PER_TENSOR "
                                    "scaling is ON", fusedConv->name().c_str());
            }
        }
    }
    else
    {
        ASSERT ( inTensorScales.size() == (size_t)inputEdges().at(0)->tensorSurfaceDesc()->dimensions().c );
        for (NvF32 its = 1; its < inTensorScales.size(); ++its)
        {
            if ( perTensorInTensorScl != inTensorScales[its] )
            {
                ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "Channel scales should be same for input, when PER_TENSOR scaling is ON");
            }
        }
    }

    for ( NvU32 bb = 0; bb < numBiasData; ++bb)
    {
        switch (origBiasBlob.type)
        {
            case nvdla::DataType::FLOAT: {
                NvF32 fp32Bias = reinterpret_cast<NvF32*>(const_cast<void*>(origBiasBlob.values))[bb];
                NvF32 biasRescaleFactor = perTensorInTensorScl;
                if ( fusedConv )
                {
                    biasRescaleFactor = perTensorInTensorScl * filterScales[bb];
                }
                scaledFP32Bias = NvF32(fp32Bias / biasRescaleFactor);
                NvS32 int32Bias = static_cast<NvS32>(std::floor(scaledFP32Bias + 0.5f));
                rescaledBias32.push_back(int32Bias);
            } break;
            case nvdla::DataType::HALF: {
                NvF32 fp16Bias = reinterpret_cast<half_float::half*>(const_cast<void*>(origBiasBlob.values))[bb];
                NvF32 biasRescaleFactor = perTensorInTensorScl;
                if ( fusedConv )
                {
                    biasRescaleFactor = perTensorInTensorScl * filterScales[bb];
                }
                scaledFP32Bias = NvF32(fp16Bias / biasRescaleFactor);
                NvS32 int32Bias = static_cast<NvS32>(std::floor(scaledFP32Bias + 0.5f));
                rescaledBias32.push_back(int32Bias);
            } break;
            default:
                ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "Can't scale bias data which is not FLOAT / HALF "
                                        "precision for %s\n", name().c_str());
        }
    }

    maxBias = *std::max_element(rescaledBias32.begin(), rescaledBias32.end(), absCompare);
    numBits = ceil(log(abs(maxBias))/log(2)) + 1;
    biasShift = std::min(SDP_LEFT_SHIFT_MAX_PLACES, std::max(0, numBits - 16));

    params().x1Params().setShiftValue(biasShift);

    for ( NvU32 bb = 0; bb < numBiasData; ++bb)
    {
	    int16Bias = static_cast<NvS16>(rescaledBias32[bb] >> biasShift);
        pInt16Bias[bb] = int16Bias;

        if ( graph()->debugQuantization() )
        {
            if (fusedConv)
            {
                gLogInfo << "rawBias/Si*Sw "
                         << reinterpret_cast<NvF32*>(const_cast<void*>(origBiasBlob.values))[bb] << " / "
                         << " ( " << perTensorInTensorScl << " * " << filterScales[bb] << " ) = "
                         << (reinterpret_cast<NvF32*>(const_cast<void*>(origBiasBlob.values))[bb]/(perTensorInTensorScl * filterScales[bb]))
                         << " -> " << rescaledBias32[bb] << " -> " << (int)int16Bias << "*2^-" << biasShift << endl;
            }
            else
            {
                gLogInfo << "rawBias/Si "
                         << reinterpret_cast<NvF32*>(const_cast<void*>(origBiasBlob.values))[bb] << " / "
                         << perTensorInTensorScl << " = "
                         << (reinterpret_cast<NvF32*>(const_cast<void*>(origBiasBlob.values))[bb]/perTensorInTensorScl)
                         << " -> " << rescaledBias32[bb] << " -> " << (int)int16Bias << "*2^-" << biasShift << endl;
            }
        }
    }

    int16BiasBlob.type   = nvdla::DataType::INT16;
    int16BiasBlob.values = pInt16Bias;
    int16BiasBlob.count  = origBiasBlob.count;

    // set scaled bias
    params().setRawBiasData(int16BiasBlob);

fail:
    return e;
}
```
6.fuseOntheFLyNodes 没大整明白这个是干嘛用的
ToDo
7.handleLowPrecisionConversion 硬件内部有和精度有关的操作，需要给相应寄存器赋值。
```c++
NvDlaError engine_ast::ConvCoreNode::handleLowPrecisionConversions()
{
    NvDlaError e = NvDlaSuccess;
    ConvCoreCVTParams convCvt;
    PrecisionCVTParams inCvt;
//精度必须为INT8模式，量化方式必须为PerTensor
    if ( graph()->profile()->computePrecision().v() != surface::SurfacePrecisionEnum::NVDLA_PRECISION_INT8 )
    {
        // nop
        goto fail;
    }
    else if ( graph()->profile()->tensorScalingMode().v() != nvdla::TensorScalingMode::PER_TENSOR )
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "Don't support tensor scaling mode: %s\n",
                                graph()->profile()->tensorScalingMode().c_str());
    }
    else if ( graph()->profile()->quantizationMode().v() != nvdla::QuantizationMode::PER_KERNEL &&
              graph()->profile()->quantizationMode().v() != nvdla::QuantizationMode::PER_FILTER )
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "Don't support quantization mode: %s\n",
                                graph()->profile()->quantizationMode().c_str());
    }
//设置相应寄存器模式
    inCvt.setEnable(1);
    inCvt.setScale(1);
    inCvt.setOffset(0);
    inCvt.setTruncate(0);

    convCvt.setInputCVT(inCvt);
    convCvt.setOutTruncate(0);
    convCvt.setPraTruncate(0);

    params().setConvCoreCVT(convCvt);

fail:
    return e;
}
```
8.translateAuxData 最终数据节点中的权重信息和偏置信息是要映射到硬件上去的，但是硬件资源有限所以要根据权重的Kernel和Mac阵列的Kernel数对权重和偏置进行切分。这里仍然以conv算子为例。
```c++

NvDlaError engine_ast::ConvCoreNode::translateAuxData()
{
    NvDlaError e = NvDlaSuccess;

    bool isIMGConv      = false;
    Edge* dataInputEdge = NULL;
    Edge* auxEdge       = NULL;
    surface::SurfacePrecision computePrecision;
    NvU32 atomicCSize = 0;
    NvU32 atomicKSize = 0;
    NvU32 cbufWidth   = 0;

    PROPAGATE_ERROR_FAIL( verifyEdgePorts() );

    computePrecision  = graph()->profile()->computePrecision();
    atomicCSize = graph()->target_config()->atomicCSize();
    atomicKSize = graph()->target_config()->atomicKSize();
    cbufWidth   = graph()->target_config()->bufEntryWidth();

    dataInputEdge = inputEdges()[0];
    auxEdge       = auxEdges()[0];

    isIMGConv = dataInputEdge->tensorSurfaceDesc()->surfaceFormat().category() == surface::SurfaceCategoryEnum::IMG;
    if (isIMGConv && NodeFactory::nodeCast<ConvCoreConvolutionOpNode*>(this)->params().postExtension() > 0)
    {
        // when post chnl extension is done for IMG conv, weights are already remapped. No need to remap them again
        ASSERT(params().DLAWeights().values != NULL);
        goto fail;
    }

    {
        Weights trnsKrnlWts;
        Weights rawKrnlWts = params().rawWeights();

        if ( graph()->debugWeights() )
        {
            gLogInfo << "translating weights for " << id() << " kernel-dims kcrs = " <<
                                    auxEdge->tensorSurfaceDesc()->dimensions().n << "," <<
                                    auxEdge->tensorSurfaceDesc()->dimensions().c << "," <<
                                    auxEdge->tensorSurfaceDesc()->dimensions().h << "," <<
                                    auxEdge->tensorSurfaceDesc()->dimensions().w << "" <<
                                    " and size= " << rawKrnlWts.count << endl;
        }


        WeightTrns::WeightDims kernelDims (rawKrnlWts.count,
                                           auxEdge->tensorSurfaceDesc()->dimensions().n,
                                           auxEdge->tensorSurfaceDesc()->dimensions().c,
                                           auxEdge->tensorSurfaceDesc()->dimensions().w,
                                           auxEdge->tensorSurfaceDesc()->dimensions().h,
                                           (int)params().stride().w,
                                           (int)params().stride().h);
        if (rawKrnlWts.count != (auxEdge->tensorSurfaceDesc()->dimensions().n *
                                 auxEdge->tensorSurfaceDesc()->dimensions().c *
                                 auxEdge->tensorSurfaceDesc()->dimensions().h *
                                 auxEdge->tensorSurfaceDesc()->dimensions().w))
        {
            ORIGINATE_ERROR_FAIL(NvDlaError_BadParameter, "kernel dims dont match kernel size ");
        }

        if ( params().convMode().v() == ConvolutionModeEnum::CONV_WINOGRAD )
        {
            PRECISION_SWITCH(rawKrnlWts.type.v(), computePrecision.v(), trnsKrnlWts, WeightTrns::translateWtsForWG,
                                                                                     kernelDims,
                                                                                     rawKrnlWts);
        }
        else if ( params().convMode().v() == ConvolutionModeEnum::CONV_DIRECT )
        {
            PRECISION_SWITCH(rawKrnlWts.type.v(), computePrecision.v(), trnsKrnlWts, WeightTrns::translateWtsForDC,
                                                                                     kernelDims,
                                                                                     rawKrnlWts,
                                                                                     atomicKSize,
                                                                                     atomicCSize,
                                                                                     cbufWidth);
        }
        else
        {
            PROPAGATE_ERROR_FAIL(NvDlaError_BadValue, "Unknown Conv mode : %s for %s",
                    params().convMode().c_str(), name().c_str());
        }

        if (trnsKrnlWts.values == NULL)
        {
            PROPAGATE_ERROR_FAIL(NvDlaError_BadValue, "Kernel Wt trnaslation failed for node '%s'", name().c_str());
        }

        params().setDLAWeights(trnsKrnlWts);
    }


fail:
    return e;
}

```
这里以DC卷积为例：
```c++
static Weights translateWtsForDC
      (
          WeightDims                 wDims,               //!<  dims of orig caffe wt blob
          Weights&                   srcWts,              //!<  ptr to orig caffe wt blob
          int atomicKSize,
          int atomicCSize,
          int cbufWidth,
          std::map<std::string, IT>& mCaffeHash = *(new std::map<std::string, IT>()) //!<  hash of the entire caffe wt blob
      )
  {
    Weights DC_tr_wts = Weights(nvdla::DataType::FLOAT, NULL, 0);

    API_CHECK_WEIGHTS_RETVAL(srcWts, DC_tr_wts);

    bool isSanityOn = mCaffeHash.size() > 0 ? true : false;
    IT* pSrcWts  = reinterpret_cast<IT*>(const_cast<void*>(srcWts.values));
    IT* pDCCEWts = pSrcWts;
    WeightDims origWDims = wDims;
    std::vector<AtomicWtOp> vWtOps;
    vWtOps.clear();

    //Channel extend if need be
    //pDCCEWts = doSlowCEForDC<IT>(wDims, pSrcWts); // FIXME: do wt chnl extension only for IMGs in a separate API

    //if (isSanityOn)
    //    if(runSanityForDCWtChnlExt<IT>(pSrcWts, origWDims, pDCCEWts, wDims))
    //        return Weights{nvdla::DataType::FLOAT, NULL, 0};

    //Prepare wt translation ops
    prepWtTrnsOpsForDC<RT>(wDims, vWtOps, atomicKSize, atomicCSize);

    //Execute wt translation ops
    DC_tr_wts = execWtTrnsOpsForDC<IT, RT>(wDims, pDCCEWts, vWtOps, atomicKSize, atomicCSize, cbufWidth);

    if (isSanityOn)
      if (runSanityForDCWtTrns<IT, RT>(reinterpret_cast<RT*>(const_cast<void*>(DC_tr_wts.values)),
                                       origWDims,
                                       vWtOps,
                                       mCaffeHash,
                                       atomicKSize,
                                       atomicCSize))
        return Weights{nvdla::DataType::FLOAT, NULL, 0};

    if (pDCCEWts != pSrcWts)
    {
      engine_ast::MemoryCollector::getInstance()->freeMemory(pDCCEWts);
      pDCCEWts = NULL;
    }

    return DC_tr_wts;
  }
```
其中最重要的两个函数为  prepWtTrnsOpsForDC<RT>(wDims, vWtOps, atomicKSize, atomicCSize);和 DC_tr_wts = execWtTrnsOpsForDC<IT, RT>(wDims, pDCCEWts, vWtOps, atomicKSize, atomicCSize, cbufWidth);分别是对数据进行切分和重排的。
9.reserveBuffer():
给tensorbufferdes预留相应的内存大小。
```c++
NvDlaError engine_ast::Edge::reserveBuffer()
{
    NvDlaError e = NvDlaError_Success;

    NvU64 existingSize = 0;
    NvU64 proposedSize = 0;
    memory::TensorCategory tc;
    memory::TensorBufferDesc* tbd;
    surface::TensorSurfaceDesc* tsd = tensorSurfaceDesc();
    NvU16 numBatches = graph()->profile()->multiBatchSize();

    if ( !isDataEdge() )
    {
        goto fail;
    }
    else if (!tsd)
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "TSD not yet registered for edge %s", id().c_str());
    }
    else if (!tsd->size())
    {
        ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "surface size == 0 for %s", tsd->id().c_str());
    }

    tbd = tsd->tensorBufferDesc();
    tc  = tsd->tensorCategory();
    existingSize = tbd->size();
    proposedSize = tsd->size();
    switch(tc.v())
    {
        case memory::TensorCategoryEnum::GLOBAL_TENSOR:
        case memory::TensorCategoryEnum::LOCAL_TENSOR:
            tbd->setSize( std::max<NvU64>(existingSize, proposedSize) );
            break;
        case memory::TensorCategoryEnum::EXTERNAL_TENSOR:
            ASSERT( bindable() );
            // adjust buffer size for multiple batches on the bindable tensor
            if ( existingSize )
            {
                tbd->setSize( std::max<NvU64>(existingSize, proposedSize * numBatches) );
            }
            else
            {
                tbd->setSize(proposedSize * numBatches);
            }
            break;
        case memory::TensorCategoryEnum::STREAM_TENSOR:
            tbd->setMemoryLoc(memory::LocationEnum::lSTREAM);
            break;

        default:
            ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "Tensor Category:%s not recognized", tc.c_str());
    }

fail:
    return e;
}
```
10.splitNodes():分配算子所需要的具体硬件资源
```c++
NvDlaError engine_ast::ConvCoreNode::splitNodesInternal()
{
    NvDlaError e = NvDlaSuccess;

    NvU32 totalDataBanksNeeded = 0;
    NvU32 totalWtBanksNeeded   = 0;
    NvU32 minWtBanksNeeded     = 0;
    NvU32 compWtReservedBank   = 0;
    NvU32 spareBanks           = 0;

    surface::TensorSurfaceDesc *srcTSD     = graph()->nodeInputTensorSurface(this, 0, supportedInSurfCategories());
    surface::TensorSurfaceDesc *weightTSD  = graph()->nodeInputTensorSurface(this, 0, supportedAuxSurfCategories());

    bool weight_compression = graph()->profile()->canCompressWeights() && graph()->target_config()->isCompressWeightsCapable();
    NvU32 totalCbuffBanks = graph()->target_config()->bufBankAllotted();

    totalDataBanksNeeded = calculateTotalBanksForData(srcTSD);
    totalWtBanksNeeded   = calculateTotalBanksForWeight(weightTSD);
    minWtBanksNeeded     = calculateMinBanksForWeight(weightTSD);
    // If weights are compressed, WMB surface needs 1 bank (Bank-15)
    compWtReservedBank   = weight_compression ? 1 : 0;

    if ( debugSplits() )
    {
        gLogInfo << "(" << name() << ") " << params().convMode().c_str() << endl;
        gLogInfo << "\ttotal b4d needed " << totalDataBanksNeeded << endl;
        gLogInfo << "\ttotal b4w needed " << totalWtBanksNeeded << endl;
        gLogInfo << "\tmin b4w needed " << minWtBanksNeeded << endl;
        gLogInfo << "\treserved WMB bank " << compWtReservedBank << endl;
        gLogInfo << "(" << name() << ") ";
    }

    /* FIXME: For now, follow the following order of preference
     *  1.  Full input and Full weight        (no split needed)
     *  2.a Full input and Partial weight     (split-k mode)
     *  2.b Partial input and Full weight     (partial-H mode)
     *  3   Partial input and Partial weight  (split-k and partial-H)
     */
    //HW-powered: FI + FW
    if (totalWtBanksNeeded + totalDataBanksNeeded + compWtReservedBank <= totalCbuffBanks)
    {
        // nothing to split
        if ( debugSplits() )
        {
            gLogInfo << "FI + FW mode. Nothing to split" << endl;
        }
        params().setAllottedDataBanks(totalDataBanksNeeded);
        params().setAllottedWeightBanks(totalWtBanksNeeded);
        goto fail;
    }

    //HW-powered: FI + ping-pong Wts
    if ((2*minWtBanksNeeded) + totalDataBanksNeeded + compWtReservedBank <= totalCbuffBanks)
    {
        if ( debugSplits() )
        {
            gLogInfo << "FI + ping-pong mode on weights" << endl;
        }
        params().setAllottedDataBanks(totalDataBanksNeeded);
        params().setAllottedWeightBanks(2*minWtBanksNeeded);
        goto fail;
    }
    //HW-powered: FI + 1KG wts
    else if (minWtBanksNeeded + totalDataBanksNeeded + compWtReservedBank <= totalCbuffBanks)
    {
        if ( debugSplits() )
        {
            gLogInfo << "FI + 1KG of weights. Suboptimal but hw automated" << endl;
        }
        params().setAllottedDataBanks(totalDataBanksNeeded);
        params().setAllottedWeightBanks(minWtBanksNeeded);
        goto fail;
    }

    /* If control reaches here, then either the data is massive and/or single KG is massive,
     * software splits are unavoidable. Everything that follows is profile governed i.e.
     * we will split nodes if the profile forces us to. A better profile later will
     * eventually emerge a better KPI. However, we do attempt to determine if any scope of
     * hw automation is still left.
     */

    /* FI within (profile) alloted banks:-
     * FI + (hw-split-k(Ping-Pong) / hw-split-k(single KG))
     */
    if (totalDataBanksNeeded < graph()->profile()->dataBanksAlloted())
    {
        if ( debugSplits() )
        {
            gLogInfo << "FI + ";
        }
        params().setAllottedDataBanks(totalDataBanksNeeded);

        // hw-split-k (Ping-Pong)
        if ((2*minWtBanksNeeded) + compWtReservedBank < graph()->profile()->weightBanksAlloted())
        {
            if ( debugSplits() )
            {
                gLogInfo << "HW split-K with Ping-pong mode on weights" << endl;
            }
            params().setAllottedWeightBanks(2*minWtBanksNeeded);
            goto fail;
        }
        // hw-split-k (single KG)
        else if (minWtBanksNeeded + compWtReservedBank < graph()->profile()->weightBanksAlloted())
        {
            if ( debugSplits() )
            {
                gLogInfo << "HW split-K with single KG" << endl;
            }
            params().setAllottedWeightBanks(minWtBanksNeeded);
            goto fail;
        }
        ORIGINATE_ERROR_FAIL(NvDlaError_NotSupported, "Not enough banks to hold weight data. No software split supported");
    }

    /* Split-Input within (profile) alloted banks:-
     * SW-partial-h + (FW (all KGs) / hw-split-k(Ping-Pong) / hw-split-k(single KG) / sw-split-k)
     */
    else
    {
        if (totalWtBanksNeeded + compWtReservedBank <= graph()->profile()->weightBanksAlloted())
        {
            if ( debugSplits() )
            {
                gLogInfo << "sw-Partial-H + FW" << endl;
            }
            params().setAllottedWeightBanks(totalWtBanksNeeded);
            spareBanks = totalCbuffBanks - totalWtBanksNeeded - compWtReservedBank;
            PROPAGATE_ERROR_FAIL(splitData(spareBanks));
        }
        // hw-split-k(Ping-Pong)
        else if ((2*minWtBanksNeeded) + compWtReservedBank <= graph()->profile()->weightBanksAlloted())
        {
            if ( debugSplits() )
            {
                gLogInfo << "sw-Partial-H + hw-split-K (ping-pong mode)" << endl;
            }
            params().setAllottedWeightBanks(2*minWtBanksNeeded);
            spareBanks = totalCbuffBanks - (2*minWtBanksNeeded) - compWtReservedBank;
            PROPAGATE_ERROR_FAIL(splitData(spareBanks));
        }
        // hw-split-k(single KG)
        else if (minWtBanksNeeded + compWtReservedBank <= graph()->profile()->weightBanksAlloted())
        {
            if ( debugSplits() )
            {
                gLogInfo << "sw-Partial-H + hw-split-K (single KG mode)" << endl;
            }
            params().setAllottedWeightBanks(minWtBanksNeeded);
            spareBanks = totalCbuffBanks - minWtBanksNeeded - compWtReservedBank;
            PROPAGATE_ERROR_FAIL(splitData(spareBanks));
        }
        //SW-poweredL sw-partial-h + hw-split-k
        else if (minWtBanksNeeded < graph()->profile()->weightBanksAlloted())
        {
            // mostly remnant code block
        }
        // sw-split-k
        else
        {
            if ( debugSplits() )
            {
                gLogInfo << "sw-Partial-H + sw-split-K" << endl;
            }
            PROPAGATE_ERROR_FAIL(splitWeightsAndData(graph()->profile()->dataBanksAlloted(), graph()->profile()->weightBanksAlloted()));
        }
    }

fail:
    return e;
}
```
11.fuseSubEngineOps():这里涉及到算子融合，与上述相同，但是具体算子融合的内容不同，具体如下：
```c++
engine_ast::Node* engine_ast::SDPNode::fuseSDPSubEngineOp(SDPNode* nextSDP)
{
    NvDlaError e = NvDlaSuccess;
    Node* removableNode = NULL;

    if (isFeasibleToFuseSDPSubEngineOp(nextSDP))
    {
        engine_ast::Edge* edgeToMoveX1 = NULL;
        engine_ast::Edge* edgeToMoveX2 = NULL;
        SDPSuperOpNode* sdpSuperOp = NULL;
        NodeSequence substituteNodes;
        NodeSequence sourceNodes;
        engine_ast::Node* eltPeerSource = NULL;

        // Create new SDP super node
        sdpSuperOp = NodeFactory::newSDPSuperOpNode(NULL, graph());
        if (!sdpSuperOp)
        {
            ORIGINATE_ERROR_FAIL(NvDlaError_InsufficientMemory, "Couldn't create new SDP super op for replacing %s and %s",
                    this->name().c_str(), nextSDP->name().c_str());
        }

        // configure this SDP op in X1 engine
        switch(engineOpType().v())
        {
            case EngineOpTypeEnum::SDP_ELEMENTWISE:
                // Do not support elt op in x1.
                // Limitation is finding the aux edge of elt in x1 i.e. differentiating betn 2 inputs edges
                goto fail;
            default:
                PROPAGATE_ERROR_FAIL(this->configureSDPSuperOpSubEngine(sdpSuperOp, SDP_ENGINE_X1));
        }

        // Find X1 Aux Edge
        PROPAGATE_ERROR_FAIL(this->nodeAuxEdge(&edgeToMoveX1));

        // configure next SDP OP in X2 engine
        PROPAGATE_ERROR_FAIL(nextSDP->configureSDPSuperOpSubEngine(sdpSuperOp, SDP_ENGINE_X2));

        // Find X2 Aux Edge
        if (nextSDP->engineOpType().v() == EngineOpTypeEnum::SDP_ELEMENTWISE)
        {
            // Aux edge of Elementwise is connecting edge betn elt and peer source
            eltPeerSource = NodeFactory::nodeCast<SDPElementWiseOpNode*>(nextSDP)->getPeerSource(this);
            edgeToMoveX2 = graph()->connectingDataEdge(nextSDP, eltPeerSource, ast::EdgeSideEnum::SECOND);
        }
        else
        {
            PROPAGATE_ERROR_FAIL(nextSDP->nodeAuxEdge(&edgeToMoveX2));
        }

        // Graph Updates
        sourceNodes = graph()->upstreamDataNodes(this);

        // 1. Replace this SDP node with Super Op node in the graph
        substituteNodes.push_back(sdpSuperOp);
        PROPAGATE_ERROR_FAIL(graph()->substituteNodeInAST(this, substituteNodes));

        // 2. Move X1 Aux Edge
        sdpSuperOp->markSdpAuxEdge(SDP_ENGINE_X1, edgeToMoveX1);
        graph()->replaceEdgeNodes(edgeToMoveX1, ast::EdgeSideEnum::SECOND, this, sdpSuperOp);

        // 3. Move X2 Aux Edge
        sdpSuperOp->markSdpAuxEdge(SDP_ENGINE_X2, edgeToMoveX2);
        graph()->replaceEdgeNodes(edgeToMoveX2, ast::EdgeSideEnum::SECOND, nextSDP, sdpSuperOp);

        // 4. nextSDP node should be removed manually, by disconnecting it from the input side
        PROPAGATE_ERROR_FAIL(graph()->removeNodeFromAST(nextSDP, IODirectionEnum::INPUT));

        // 5. Framework will remove this SDP node
        removableNode = this;

        if (sourceNodes.size() != 0)
        {
            if ( graph()->debugFuseSubEngineOps() )
            {
                gLogInfo << "SDP x2 fusion parent: " << sourceNodes[0]->name() << std::endl;
            }
            PROPAGATE_ERROR_FAIL(sourceNodes[0]->fuseOnTheFlyNodes());

            if (eltPeerSource && dependencyParams().fusedNode(IODirectionEnum::INPUT) == sourceNodes[0])
            {
                // for elt x2 fusion, add compute edge betn elt sources.
                // This gurantees that SDPSuperOp fused parent will always be
                // traversed last.
                Edge* compEdge = graph()->addComputeEdge(eltPeerSource, sourceNodes[0]);
                if ( graph()->debugFuseSubEngineOps() )
                {
                    gLogInfo << "elt x2 fusion compute edge " << compEdge->id();
                    gLogInfo << " betn " << eltPeerSource->name();
                    gLogInfo << " & " << sourceNodes[0]->name() << std::endl;
                }
            }
        }
    }
fail:
    return removableNode;
}
```
12.boundGraph():这里什么都没做!
13.handleMultiBatch():这里针对每个算子每个Tensor针对多个batch的情况进行资源复用的设置。
还是以conv算子为例：
```c++
/*------------------------------Handle Multi-Batch---------------------*/
NvDlaError engine_ast::ConvCoreNode::handleMultiBatch()
{
    NvDlaError e = NvDlaSuccess;

    NvU32 numBatches = graph()->profile()->multiBatchSize();
    NvU32 firstBatch = 0;
    NvU32 lastBatch  = numBatches - 1;
    surface::TensorSurfaceDesc *weightTSD = NULL;

    for (NvU32 nn = 1; nn < numBatches; ++nn)
    {
        params(nn) = params(0);
        switch(engineOpType().v()) {
            case EngineOpTypeEnum::CONVOLUTION_CONV:
                NodeFactory::nodeCast<ConvCoreConvolutionOpNode*>(this)->params(nn) =
                        NodeFactory::nodeCast<ConvCoreConvolutionOpNode*>(this)->params(0);
                break;
            case EngineOpTypeEnum::CONVOLUTION_FC:
                NodeFactory::nodeCast<ConvCoreFullyConnectedOpNode*>(this)->params(nn) =
                        NodeFactory::nodeCast<ConvCoreFullyConnectedOpNode*>(this)->params(0);
                break;
            case EngineOpTypeEnum::CONVOLUTION_DECONV:
                NodeFactory::nodeCast<ConvCoreDeconvolutionOpNode*>(this)->params(nn) =
                        NodeFactory::nodeCast<ConvCoreDeconvolutionOpNode*>(this)->params(0);
                break;
            default:
                ORIGINATE_ERROR_FAIL(NvDlaError_BadValue, "Unsupported CONV Engine Op type: %s", engineOpType().c_str());
        }
    }

    /* Convolution ops can have weight reuse scenarios, handle them carefully among batches
     *
     * Whenever the entire weights for the conv - op can be fit in the conv_buff banks,
     * subsequent batches can reuse those weights.
     *
     * Whenever, there is hardware automated split-K selected (ping-pong mode(2KG) OR 1KG),
     * weight reuse among batches is not possible. So the weights have to be re-fetched
     * separately for each batch.
     */
    weightTSD = graph()->nodeInputTensorSurface(this, 0, supportedAuxSurfCategories());
    if (params(firstBatch).weightBanksAllotted() == calculateTotalBanksForWeight(weightTSD))
    {
        bool isSingleBatchWtRls = params(firstBatch).isReleaseWeights();
        for (NvU32 nn = firstBatch; nn < lastBatch; ++nn)
        {
            NvU32 currBatch = nn;
            NvU32 nextBatch = nn + 1;
            params(nextBatch).setReuseWeights(true);
            params(currBatch).setReleaseWeights(false);
        }
        params(lastBatch).setReleaseWeights(isSingleBatchWtRls);
    }

fail:
    return e;
}
```
然后输出engine_1.json文件
```c++
    if ( dumpEmittedGraph )
    {
        dump_eng.setGraphId("engine_1");
        dump_eng.setFilename("engine_1.json");
        PROPAGATE_ERROR_FAIL( dump_eng.visitElems(g.back()->scoredOrdering()));
    }
```
如果在profile中copyOutDebugSurface参数被开启：
那么执行enableCopyOutDebugSurface()这个选项在默认的编译参数中没有被开启这里不做考虑。
14.generateDependencyParams()生成硬件直接的参数
15.resolveMemory 为tensor分配相应的内存大小，profile中有内存池的定义

### 4.3.7.代码流程分析-EngineAST到后端代码Emit（代码生成）
上述pass执行完后执行 PROPAGATE_ERROR_FAIL( emit(final_g, l) );生成loadable序列化文件
1.首先分析一下后端生成代码中重要的数据结构：
DLAInterface和EMUInterface分别代表加速器接口和模拟器接口
```c++
    DLAInterface *dla_if = 0;
    EMUInterface *emu_if = 0;
```
跟Loadable有关的重要数据接口,主要包括六个部分，task,submit,event，reloc，memory和address。
```c++
vector<ILoadable::TaskListEntry> task_list_entries;
vector<ILoadable::SubmitListEntry> submit_list_entries;
vector<ILoadable::EventListEntry> event_list_entries;
vector<ILoadable::RelocEntry> reloc_entries;
```
task主要分为两个部分，分别递交给加速器和EMU即CPU，后端也是根据task划分任务类型，进一步submit和处理event.submit则是内核态与用户态交互的形式，交互具体内容为event，交互的数据存放在特定的内存空间中。内存空间则是runtime根据loadable中的address和memory确定的。
```c++
struct TaskListEntry
    {
        NvU16 id;
        NvU32 interface; // DLA interface id
        static inline NvU32 interface_NONE() { return Interface_NONE; }
        static inline NvU32 interface_DLA1() { return Interface_DLA1; }
        static inline NvU32 interface_EMU1() { return Interface_EMU1; }

        NvS16 instance; // -1 := for any available
        static inline NvS16 instance_ANY() { return -1; }

        std::vector<NvU16> preactions;   // [event id]...
        std::vector<NvU16> postactions;  // [event id]...
        std::vector<NvU16> address_list; // [addr list id]...[addr list id]
        TaskListEntry(const TaskListEntry &o) :
            id(o.id),
            interface(o.interface),
            instance(o.instance),
            preactions(o.preactions),
            postactions(o.postactions),
            address_list(o.address_list) { }

        TaskListEntry() : id(0),
                          interface(Interface_NONE),
                          instance(-1),
                          preactions(),
                          postactions(),
                          address_list() { }
    };
```
2.Loadable六个部分具体生成方式
首先是MemoryList,首先对内存池中tensorbuffer分配内存地址以及大小。
```c++
static NvDlaError addMemEntriesForPools
(
    engine_ast::Graph* g,
    vector< Loadable::MemoryListEntry >& graphMemObjects,
    NvS16& memId,
    vector< Loadable::AddressListEntry>& graphAddrObjects,
    NvS16& addrId
)
{
    NvDlaError e = NvDlaSuccess;
    vector< memory::Pool > *memPools = g->resourceMgr()->memoryPools();

    for ( size_t pid = 0; pid < memPools->size(); ++pid )
    {
        memory::Pool &pool = (*memPools)[pid];

        memory::LocationEnum location = pool.location().e();
        memory::PoolTypeEnum poolType = pool.type().e();
        NvU8 domain;
        NVDLA_UNUSED(poolType);

        // we only care about actual memory
        switch (location)
        {
            case memory::LocationEnum::lCVSRAM:
                domain = ILoadable::MemoryDomain_SRAM;
                break;

            case memory::LocationEnum::lDRAM:
                domain = ILoadable::MemoryDomain_SYSMEM;
                break;

            default:
                continue;
        }

        // don't bother if it is empty.
        if ( !pool.sizeUsed() )
        {
            continue;
        }

        pool.setMemoryId(memId++);
        pool.setAddressId(addrId++);

        Loadable::MemoryListEntry memEntry;

        memEntry.id        = pool.memoryId();
        memEntry.size      = NvU64(4096) * ((pool.sizeUsed() + NvU64(4095))/NvU64(4096));
        memEntry.alignment = 4096; // page size
        memEntry.domain    = domain;
        memEntry.flags     = Loadable::MemoryListEntry::flags_alloc();


        if ( pool.contents().begin() != pool.contents().end() )
        {
            set<surface::TensorSurfaceDesc *>::iterator ci;
            memEntry.flags |= Loadable::MemoryListEntry::flags_set();

            for (ci = pool.contents().begin(); ci != pool.contents().end(); ++ci )
            {
                // tbd: sort these for repeatability
                memory::TensorBufferDesc *tbd = (*ci)->tensorBufferDesc();
                if ( !tbd )
                {
                    THROW_ERROR(NvDlaError_InvalidState);
                }
                memEntry.contents.push_back(tbd->id());
                memEntry.offsets.push_back((*ci)->bufferOffset() + tbd->poolOffset());
            }
        }

        if ( g->debugMemoryLayout() )
        {
            gLogInfo << "(Pool) Memory list entry=" << memEntry.id << " size=" << memEntry.size <<
                " used=" << pool.sizeUsed() << " domain=" << (int)memEntry.domain << " flags=" << (int)memEntry.flags << endl;
            for ( size_t ci=0; ci < memEntry.contents.size(); ++ci )
            {
                gLogInfo << "\tcontent: " << memEntry.contents[ci] << " @ " << memEntry.offsets[ci] << endl;
            }
            gLogInfo << endl;
        }

        graphMemObjects.push_back(memEntry);
        {
            Loadable::AddressListEntry addrEntry;
            addrEntry.id     = pool.addressId();
            addrEntry.mem_id = memEntry.id;
            addrEntry.offset = 0;
            addrEntry.size   = memEntry.size;
            graphAddrObjects.push_back(addrEntry);
        }
    }
```
在调度任务前，NVDLA编译器首先给出DLA和CPU的设备号的接口信息
```
compiler targeting dla (fw) interface 0.12
compiler targeting emu (cpu) interface 0.0
```
紧接着分配内存接口，主要分pool，buffer。然后为内存分配相应的地址接口。在为buffer定义内存空间的时候还要对输入输出的tensor分配内存大小。debug信息中如果是对输入输出张量定义内存大小会有（bindable）(buffer)的标志。
```c++
    // each memory pool gets an id.  pools need to come before buffers
    // because buffers can and will use the pools' memory ids as needed.
    //
    PROPAGATE_ERROR_FAIL(addMemEntriesForPools(this, graphMemObjects, memId, graphAddrObjects, addrId));

    //
    // create memory id entries for non-pooled buffers
    //
    PROPAGATE_ERROR_FAIL(addMemEntriesForBuffers(this, graphMemObjects, tensorDescEntries, memId));

    //
    // surfaces generate address id entries
    //
    PROPAGATE_ERROR_FAIL(addAddrEntriesForSurfaces(l, this, graphAddrObjects, addrId));
```
```
(Pool) Memory list entry=1 size=925696 used=924288 domain=0 flags=3
content: tb-0 @ 0
content: tb-2 @ 4096
content: tb-3 @ 32768
content: tb-4 @ 8192
content: tb-5 @ 524288
content: tb-6 @ 12288
content: tb-8 @ 16384
content: tb-9 @ 24576

(Pool) Memory list entry=2 size=49152 used=46080 domain=0 flags=1
create tensor desc precision=1 category=1 sf=12
name : data
n,c,h,w : 1,4,28,28
data format : 2
data type : 4
data category: 0
pixel format : 12
pixel mapping: 0
strides : 1 128 0 00 0 0 0
::Buffer bindId(buffer=tb-1) [ ::Surface surface=tsd-1: bindable=1
tsd-1 bind_id=1
::Surface surface=tsd-1: bindable=1
::Surface bindId(tsd-1, 0) -> 0
]
create tensor desc precision=1 category=3 sf=63
name : prob
n,c,h,w : 1,10,1,1
data format : 3
data type : 4
data category: 2
pixel format : 36
pixel mapping: 0
strides : 1 32 32 00 0 0 0
::Buffer bindId(buffer=tb-22) [ ::Surface surface=tsd-22: bindable=1
tsd-22 bind_id=1
::Surface surface=tsd-22: bindable=1
::Surface bindId(tsd-22, 1) -> 0
]
(Bindable)(Buffer) Memory list entry for tbd=tb-1:0 : 0 size=3584 domain=0 flags=5
(Bindable)(Buffer) Memory list entry for tbd=tb-22:0 : 0 size=32 domain=0 flags=9
(Surface) Address list entry for tsd=tsd-0/tb-0:0 -> 1 offset=0 size=2048
(Surface) Address list entry for tsd=tsd-1/tb-1:0 -> 3 offset=0 size=3584
(Surface) Address list entry for tsd=tsd-11/tb-11:0 -> 2 offset=0 size=18432
(Surface) Address list entry for tsd=tsd-12/tb-12:0 -> 2 offset=32768 size=4608
(Surface) Address list entry for tsd=tsd-14/tb-14:0 -> 2 offset=40960 size=4096
(Surface) Address list entry for tsd=tsd-15/tb-15:0 -> 2 offset=45056 size=1024
(Surface) Address list entry for tsd=tsd-19/tb-19:0 -> 2 offset=40960 size=512
set symbol content name=tb-2 size=40
(Surface) Address list entry for tsd=tsd-2/tb-2:0 -> 1 offset=4096 size=40
(Surface) Address list entry for tsd=tsd-21/tb-21:0 -> 2 offset=45056 size=32
(Surface) Address list entry for tsd=tsd-22/tb-22:0 -> 4 offset=0 size=32
set symbol content name=tb-3 size=25088
(Surface) Address list entry for tsd=tsd-3/tb-3:0 -> 1 offset=32768 size=25088
set symbol content name=tb-4 size=100
(Surface) Address list entry for tsd=tsd-4/tb-4:0 -> 1 offset=8192 size=100
set symbol content name=tb-5 size=400000
(Surface) Address list entry for tsd=tsd-5/tb-5:0 -> 1 offset=524288 size=400000
set symbol content name=tb-6 size=1000
(Surface) Address list entry for tsd=tsd-6/tb-6:0 -> 1 offset=12288 size=1000
set symbol content name=tb-8 size=5120
(Surface) Address list entry for tsd=tsd-8/tb-8:0 -> 1 offset=16384 size=5120
set symbol content name=tb-9 size=20
(Surface) Address list entry for tsd=tsd-9/tb-9:0 -> 1 offset=24576 size=20
```
随后，编译日志会输出task信息，具体有几个task，每个task中几个算子。算子内的参数怎么样。
```
emit discovered 2 tasks
the initial mem list size is 4 entries
the initial addr list size is 4 entries
task_id=0 has 10 op slots and 1 batches
task_id=1 has 1 op slots and 1 batches
```
task结构体里主要有如下几个部分,分别表示不同task的不同表现形式
```c++
      string network_desc_symbol   = task_id_ss.str() + "-addr0";
      string dep_container_symbol  = task_id_ss.str() + "-dep_graph";
      string op_container_symbol   = task_id_ss.str() + "-op_list";
      string surf_container_symbol = task_id_ss.str() + "-surf_list";
      string lut_container_symbol  = task_id_ss.str() + "-lut_list";
```
```
set symbol content name=task-0-addr0 size=40
set symbol content name=task-0-dep_graph size=360
set symbol content name=task-0-op_list size=1160
set symbol content name=task-0-surf_list size=6440
set symbol content name=task-0-lut_list size=700
```
然后将这些数据和内存空间保存到Loadable的blob中
```
loadable->setSymbolContent(network_desc_symbol,   network_desc_blob,   (NvU8*)network_desc_mem);
loadable->setSymbolContent(dep_container_symbol,  dep_container_blob,  (NvU8*)dep_container_mem);
loadable->setSymbolContent(op_container_symbol,   op_container_blob,   (NvU8*)op_container_mem);
loadable->setSymbolContent(surf_container_symbol, surf_container_blob, (NvU8*)surf_container_mem);
loadable->setSymbolContent(lut_container_symbol,  lut_container_blob,  (NvU8*)lut_container_mem);
```
任务执行的地址顺序如下
```c++
if ( debugTasks() )
{
    gLogInfo << "\ttask address list (indices into global address list): " << endl;
    for ( size_t ii = 0; ii < taskAddrList.size(); ++ii)
    {
        gLogInfo << "\t\t" << taskAddrList.at(ii) << endl;
    }
    gLogInfo << "\t\t<>" << endl;
}
```
```
task address list (indices into global address list):
5
1
2
3
4
6
7
8
9
10
<>
task address list (indices into global address list):
11
1
2
3
4
12
13
14
15
16
<>
```


