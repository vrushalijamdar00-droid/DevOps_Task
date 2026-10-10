module "vpc" {
  source = "./modules/vpc"

  vpc_cidr             = "10.0.0.0/16"
  vpc_name             = "devops-vpc"
  
}