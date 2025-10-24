# ZKTecoEmulator

`ZKTecoEmulator` is an unofficial emulator of zksoftware attendance device.

## Installation

There are two installation methods you can use below:

*1. Download ready-to-run binary from release*

1. Download the `zkteco-v1.0.0-linux-x86_64.elf` binary to your preferred directory.

2. Give execute permission:

    ```sh
    chmod +x zkteco-v1.0.0-linux-x86_64.elf
    ```

3. Run the binary:

    ```sh
    ./zkteco-v1.0.0-linux-x86_64.elf
    ```

4. After running, access the web UI by opening your browser to:
     
   [http://localhost:5000](http://localhost:5000)




*2. Clone and append the path of this project (recommended for development)*

1. Clone repository

    ```sh
    git clone https://github.com/u0x137/ZKTecoEmulator.git
    ```

2. Change to the project directory

    ```sh
    cd ZKTecoEmulator
    ```

3. Create virtual environment

    ```sh
    python3 -m venv venv
    ```

4. Activate virtual environment

    ```sh
    source venv/bin/activate
    ```

5. Install requirements

    ```sh
    pip install -r requirements.txt
    ```

6. Run the application

    ```sh
    python3 run.py
    ```

7. Access the web UI

    After running, access the web UI by opening your browser to:
    http://localhost:5000

## Emulated devices
    Firmware Version : Ver 6.21 Nov 19 2008
    Platform : ZEM500
    DeviceName : U580

    Firmware Version : Ver 6.60 Apr 9 2010
    Platform : ZEM510_TFT
    DeviceName : T4-C

    Firmware Version : Ver 6.60 Dec 1 2010
    Platform : ZEM510_TFT
    DeviceName : T4-C

    Firmware Version : Ver 6.60 Mar 18 2011
    Platform : ZEM600_TFT
    DeviceName : iClock260

    Platform         : ZEM560_TFT
    Firmware Version : Ver 6.60 Feb  4 2012
    DeviceName       :

        Firmware Version : Ver 6.60 Oct 29 2012
    Platform : ZEM800_TFT
    DeviceName : iFace402/ID

    Firmware Version : Ver 6.60 Mar 18 2013
    Platform : ZEM560
    DeviceName : MA300

    Firmware Version : Ver 6.60 Dec 27 2014
    Platform : ZEM600_TFT
    DeviceName : iFace800/ID

    Firmware Version : Ver 6.60 Nov 6 2017 (remote tested with correct results)
    Platform : ZMM220_TFT
    DeviceName : (unknown device) (broken info but at least the important data was read)

    Firmware Version : Ver 6.60 Jun 9 2017
    Platform : JZ4725_TFT
    DeviceName : K20 (latest checked correctly!)

    Firmware Version : Ver 6.60 Aug 23 2014
    Platform : ZEM600_TFT
    DeviceName : VF680 (face device only, but we read the user and attendance list!)

    Firmware Version : Ver 6.70 Feb 16 2017
    Platform : ZLM30_TFT
    DeviceName : RSP10k1 (latest checked correctly!)

    Firmware Version : Ver 6.60 Jun 16 2015
    Platform : JZ4725_TFT
    DeviceName : iClock260

    Firmware Version : Ver 6.60 Jun 16 2015
    Platform : JZ4725_TFT
    DeviceName : K14 (not tested, but same behavior like the other one)

    Firmware Version : Ver 6.60 Jun 5 2015
    Platform : ZMM200_TFT
    DeviceName : iClock3000/ID

    Firmware Version : Ver 6.70 Jul 12 2013
    Platform : ZEM600_TFT
    DeviceName : iClock880-H/ID
