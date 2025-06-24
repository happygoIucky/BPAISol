variable "byteplus_access_key" {
  description = "Your BytePlus Access Key"
  type        = string
  sensitive   = true
}

variable "byteplus_secret_key" {
  description = "Your BytePlus Secret Key"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "BytePlus region"
  type        = string
  default     = "ap-southeast-1"
}
