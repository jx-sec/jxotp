yum install epel-release pam pam-devel gcc python-devel  python-pip git -y
git clone https://github.com/jx-sec/pam-python-ipcpu.git
cd pam-python-ipcpu/
make lib
cp src/build/lib.*/pam_python.so /lib64/security/
cd ..
cp jxotp_auth.py /lib64/security/



