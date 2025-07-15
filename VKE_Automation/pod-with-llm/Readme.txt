Requirements
- Ensure you have pip3 install requests, kubectl and terraform installed before moving on 

1) First, change the parameters (ak/sk) accoridngly in your "1. vke.tf". Take down the vpcid and subnetid as you will need it later in step3
2) Second, please change parameters accordingly on "1.nfs-create.py" such as your ak and sk. After run, please take down your filesytemID as you will need it later in step2.
3) Third, replace the filesystemid, vpcid, subnetid and run "3. nfs-mount-and-permission.py"
4) Fourth, change the filesystemid and run "4. pv.yaml"
5) Firth, run the "5. pvc.yaml"
6) choose either 6.1 or 6.2 to test
7) bash "curl-chat.sh" to see result

Others
- If u run the vke.tf for the first time and get error on add-on, please run again terraform apply as the NAT might still be loading,only until the nodes have internet access, the add-on can be successful
- Add-on service requires nodes to be able to acccess internet. Either u use EIP attached or NAT SNAT
- If kubeconfig does not copy to your local PC, kindly run "terraform output -raw kubeconfig > ~/.kube/config" after the successful deployment