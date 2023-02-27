# AWS_Instances_Status_Report_Generator

The code is going to generate an excel sheet showing the status of the EC2 instances as healthy, unhealthy or stopped based on the instance status checks and system status checks.
Also, a PDF will be generated consisting of CPU utilization graphs.

Edit the code to add the paths to the respective folders and add
1. AWS Region
2. Access Key and Secret access key
3. sender and reciver of emails

Note:
Since, Google no longer supports less secure apps, main.py may not work.
Use csv_pdf_with_cpu_utilization.py to generate the report
