
1. add-on service requires nodes to be able to acccess internet. Either u use EIP attached or NAT SNAT
2. if u run first time and get error on add-on, please run again terraform apply as the NAT might still be loading,only until the nodes have internet access, the add-on can be successful
3. output your kubeconfig to your laptop folder. terraform output -raw kubeconfig > ~/.kube/config Here, I am using Mac thus please fill in accordingly. e.g. /Users/whoami/.kube/config"
4. ensure u already have pip3 install requests, kubectl and terraform installed before moving on 
5. After the VKE is up. Proceed to create NAS which we will need it for PV later. python nas-creation.py", Take note on the filesystemid in output.