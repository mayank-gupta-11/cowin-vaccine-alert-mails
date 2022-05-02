# cowin-vaccine-alert-mails

This Project was created to Provide alert notification mails on vaccine slot availbility to the registered Users. The idea was very simple, we have a website hosted in S3 bucket on top of Cloudfront where user needs to visit that website and provide thier email id and area pin and then just click on register button to register it.
and then our backend process will be running everyday at certain times and will provide the notification alert mails to the registered users.

the project can be splitted in two process, one is where we register the user details through API gateway and Lambda functions and then the other process which run everyday at a certain time and checks for slot availbility from official govt site and in case of slot availbility provides the alert mails to the registered users.

