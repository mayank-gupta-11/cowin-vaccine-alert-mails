import json
import boto3
import requests
import re 

regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
lambda_path = "/tmp/"

client = boto3.client('s3')
sns_client = boto3.client('sns')
s3 = boto3.resource('s3')
client_api = boto3.client('apigateway')
client_lambda = boto3.client('lambda')

def update_area_pins_env_variable(new_area_pin_list):
    
    response_lambda = client_lambda.update_function_configuration(
    FunctionName='get-vaccination-slot-details',
    Environment={
        'Variables': {
            'registered_area_pins': new_area_pin_list
        }
    }
    )
    print(response_lambda)
    
def read_area_pins_env_variable():
    
    response_lambda = client_lambda.get_function_configuration(
    FunctionName='get-vaccination-slot-details'
    )
    
    env_var = response_lambda.get('Environment').get('Variables')
    registered_area_pins = env_var.get('registered_area_pins')
    
    return eval(registered_area_pins)

def update_env_variable(blocked_ip_add,visited_ip_add):
    
    response_lambda = client_lambda.update_function_configuration(
    FunctionName='api-triggers-lambda',
    Environment={
        'Variables': {
            'blocked_ip_add': blocked_ip_add,
            'visited_ip_add':visited_ip_add
        }
    }
    )
    print(response_lambda)

def read_env_variable():
    
    response_lambda = client_lambda.get_function_configuration(
    FunctionName='api-triggers-lambda'
    )
    
    env_var = response_lambda.get('Environment').get('Variables')
    blocked_ip_add = env_var.get('blocked_ip_add')
    visited_ip_add = env_var.get('visited_ip_add')
    
    return blocked_ip_add,visited_ip_add

def deploy_the_api_wd_updated_policy():
    response = client_api.create_deployment(
    restApiId='pt5u9bxa5g',
    stageName='dev',
    stageDescription='updated the resource policy for dev',
    description='updated the resource policy'
    )
    print(response)

def update_rest_api_policy(block_this_ip):
    
    blocked_ip_add,visited_ip_add = read_env_variable()
    
    f = open(lambda_path + "blocked_ip_add.txt","r")
    blocked_ip_add = f.read()
    print(blocked_ip_add,type(blocked_ip_add))
    
    curr_blocked_ip_add = eval(blocked_ip_add)
    
    print('curr_blocked_ip_add : ',curr_blocked_ip_add)
    
    curr_blocked_ip_add.append(block_this_ip)
    new_block_list = curr_blocked_ip_add
    new_block_list = set(new_block_list)
    new_block_list = list(new_block_list)
    
    print('new_block_list : ',new_block_list)
    
    # policy wd referer and sourceip block
    res_policy = { "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Principal": "*", "Action": "execute-api:Invoke", "Resource": [ "arn:aws:execute-api:ap-south-1:328864072647:pt5u9bxa5g/*/POST/", "arn:aws:execute-api:ap-south-1:328864072647:pt5u9bxa5g/*/OPTIONS/" ], "Condition": { "StringLike": { "aws:Referer": "https://d1isozjijxpfgo.cloudfront.net/" } } }, { "Effect": "Deny", "Principal": "*", "Action": "execute-api:Invoke", "Resource": [ "arn:aws:execute-api:ap-south-1:328864072647:pt5u9bxa5g/*/POST/", "arn:aws:execute-api:ap-south-1:328864072647:pt5u9bxa5g/*/OPTIONS/" ], "Condition": { "IpAddress": { "aws:SourceIp": "192.149.172.127/32" } } } ] }
    
    
    res_policy['Statement'][1]['Condition']['IpAddress']['aws:SourceIp'] = new_block_list
    updated_policy = json.dumps(res_policy)
    print(updated_policy)
    #updated_policy = '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": "*", "Action": "execute-api:Invoke", "Resource": "arn:aws:execute-api:ap-south-1:328864072647:8i7br2mmt7/*/POST/"}, {"Effect": "Deny", "Principal": "*", "Action": "execute-api:Invoke", "Resource": "arn:aws:execute-api:ap-south-1:328864072647:8i7br2mmt7/*/POST/", "Condition": {"IpAddress": {"aws:SourceIp": ["198.51.100.0/24", "198.43.122.0/24"]}}}]}'
    
    response = client_api.update_rest_api(
    restApiId='pt5u9bxa5g',
    patchOperations=[
        {
            'op': 'replace',
            'path': '/policy',
            'value': updated_policy
        },
    ]
    )
    
    blocked_ip_add = str(new_block_list)
    
    # update the environment variable with new values
    update_env_variable(blocked_ip_add,visited_ip_add)
    
    # write the updated block list of ip add in built in file
    f = open(lambda_path + "blocked_ip_add.txt","w+")
    f.write(blocked_ip_add)
    f.close()
    
    return blocked_ip_add

def validate_source_ip(ip_add):
    
    flag = 0
    ip_add = str(ip_add) + '/32'
    print(ip_add)
    
    # read the env variables
    blocked_ip_add,visited_ip_add = read_env_variable()
    
    # read the in built in file containing visited ip add details
    f = open("visited_ip_add.txt","r")
    visited_ip_add = f.read()
    print(visited_ip_add,type(visited_ip_add))
    
    dict = eval(visited_ip_add)
    print("curr_ip_count :",visited_ip_add,type(visited_ip_add))
    
    if ip_add in dict:
        dict[ip_add] = dict[ip_add] + 1
        if dict[ip_add] > 15:
            flag = 1
            blocked_ip_add = update_rest_api_policy(ip_add)
            deploy_the_api_wd_updated_policy()
    else:
        dict[ip_add] = 1
        
    print(dict)
    visited_ip_add = str(dict)
    
    # update the environment variable with new values
    update_env_variable(blocked_ip_add,visited_ip_add)
    
    # write the updated block list of ip add in built in file
    f = open(lambda_path + "visited_ip_add.txt","w+")
    f.write(blocked_ip_add)
    f.close()
    
    return flag
    

def validate_pincode(pin):
    pin = str(pin)
    pin = pin.replace(' ','')
    
    if len(pin) > 0:
        # https://api.postalpincode.in/pincode/110001
        url = "https://api.postalpincode.in/pincode/" + str(pin)
        print("validate pin code from : ",url)
        res = requests.get(url)
        pincode_validaton_res = json.loads(res.text)
        pincode_validaton_res = pincode_validaton_res[0]
        print(pincode_validaton_res)
        
        status_of_pincode = pincode_validaton_res.get('Status')
        if status_of_pincode == 'Success':
            return 'valid'
    
    return 'invalid'

def save_area_pin_details(area_pin):
    
    # read the current area pin detail from env variable
    current_pins = read_area_pins_env_variable()
    print("current_pins :",current_pins)
    
    # adding new area pins
    current_pins = current_pins + area_pin
    current_pins = set(current_pins)
    current_pins = list(current_pins)
    
    print("new_pins :",current_pins)
    
    # save the new pin with existing pins in env variables
    data = str(current_pins)
    update_area_pins_env_variable(data)

def subscribe_the_user(email,topic_arn):
    
    subscribe_response = sns_client.subscribe(
    TopicArn=topic_arn,
    Protocol='email',
    Endpoint=email
    )

def fetch_details_from_topic(response,email,topic_arn):
    description = ''
    
    for i in response['Subscriptions']:
        print(i.get('SubscriptionArn'),i.get('Endpoint'))
        status = i.get('SubscriptionArn')
        endpoint = i.get('Endpoint')
        
        if email.lower() == endpoint.lower():
            if status == 'Deleted':
                subscribe_the_user(email,topic_arn)
                description = 'You have been Registered again, Kindly confirm the Subsription sent to your Email Id.'
                
            elif status == 'PendingConfirmation':
                subscribe_the_user(email,topic_arn)
                description = 'We have previously sent a Confirmation mail, sending again... kindly Confirm it.'
                
            else:
                description = 'You are already Registered!!'
            
            return 1,description
    
    return 0,description

def validate_email(email):
    
    if(re.search(regex, email)):
        print("Valid Email")
        return 'valid'
    else:
        print("Invalid Email")
        return 'invalid'


def lambda_handler(event, context):
    
    try:
        print(event)
        ip_check = validate_source_ip(event['sourceIP'])
        # disabling ip check 
        #ip_check = 0
        
        if ip_check == 0:
        
            data_to_be_register = event['body']
            area_pin = data_to_be_register['pin']
            email = data_to_be_register['email'].lower()
            
            area_pin = area_pin.split(',')
            print(area_pin)
            
            valid_area_pins = []
            final_description = ''
            description = ''
            flag = 0
            #email = 'gmayank10@yahoo.com'
            #pin = '208020'
            
            #####################... Validate the Email ID ...######################
            
            email_status = validate_email(email)
            
            if email_status == 'valid':
                
                #####################... register the email in sns topic ...#####################
                
                for pin in area_pin:
                    
                    pin_status = validate_pincode(pin)
                    
                    if pin_status == 'valid':
                        
                        valid_area_pins.append(pin)
                        topic_name = 'vaccination-alert-for-' + str(pin)
                        print('topic name : ',topic_name)
                        
                        ct_response = sns_client.create_topic(
                        Name=topic_name,
                        Attributes={
                            'DisplayName': topic_name
                        }
                        )
                        print(ct_response)
                        
                        topic_arn = ct_response.get('TopicArn')
                        
                        response = sns_client.list_subscriptions_by_topic(
                        TopicArn=topic_arn
                        )
                        print('response of lsbt :',response)
                        
                        while(1):
                            
                            if 'NextToken' not in response:
                                flag,description = fetch_details_from_topic(response,email,topic_arn)
                                break
                            else:
                                flag,description = fetch_details_from_topic(response,email,topic_arn)
                                
                                if flag == 1:
                                    break
                                else:
                                    token = response['NextToken']
                                    response = sns_client.list_subscriptions_by_topic(
                                    TopicArn=topic_arn,
                                    NextToken=token
                                    )
                                    
                        if flag == 1:
                            print(flag,description)
                        else:
                            subscribe_the_user(email,topic_arn)
                            description = 'Your Registration is Successful! Please Confirm the Subsciption mail, sent to your Email Id.'
                            print(flag,description)
                        
                        final_description = final_description + description + '.. ' + str(pin) + '<br>'
                    
                    else:
                        final_description = 'Invalid pin Entered... ' + str(pin) + '<br>'
                
                #####################... save the area pin details in s3 ...#####################
                
                save_area_pin_details(valid_area_pins)
            else:
                final_description = 'Invalid Email ID Entered... '  + '<br>'
        else:
            final_description = 'You have exceeded the maximum no of trials..'

        return {
            'statusCode': 200,
            'body': final_description
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 200,
            'body': json.dumps('Registration Failed!'+'<br>'+str(e))
        }