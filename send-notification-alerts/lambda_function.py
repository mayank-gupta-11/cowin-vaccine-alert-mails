import json
import requests
import json
import time
import boto3

import datetime 

regular_format = str(datetime.datetime.now())
portal_format = str(datetime.datetime.strptime(regular_format.split(' ')[0], '%Y-%m-%d').strftime('%d-%m-%y'))

client = boto3.client('sns')
s3 = boto3.resource('s3')
client_lambda = boto3.client('lambda')

def read_env_variable():
    
    response_lambda = client_lambda.get_function_configuration(
    FunctionName='get-vaccination-slot-details'
    )
    
    env_var = response_lambda.get('Environment').get('Variables')
    registered_area_pins = env_var.get('registered_area_pins')
    
    print('registered_area_pins :',registered_area_pins)
    
    return eval(registered_area_pins)

def send_sns(final_list,pin):
    
    topic_arn = 'arn:aws:sns:ap-south-1:328864072647:vaccination-alert-for-' + str(pin)
    print(topic_arn)
    msg = final_list
    
    response = client.publish(
    TopicArn=topic_arn,
    Message=msg,
    Subject='Slot Availibility in '+str(pin)
    )
    
def get_area_pins_from_topic():
    
    pins = []
    
    response = client.list_topics(
    )
    print(response)
    
    while(1):
        if 'NextToken' not in response:
            for i in response['Topics']:
                #print(i['TopicArn'])
                arn = i['TopicArn']
                pin = arn.split('-')[-1]
                print(pin)
                if len(pin) == 6:
                    pins.append(pin)
            break
        else:
            for i in response['Topics']:
                #print(i['TopicArn'])
                arn = i['TopicArn']
                pin = arn.split('-')[-1]
                print(pin)
                if len(pin) == 6:
                    pins.append(pin)
            token = response['NextToken']
            response = client.list_topics(
                NextToken=token
            )
            print(response)
            
    print(pins)
    return pins
    
    

def lambda_handler(event, context):
    # TODO implement
    print(event)
    
    #bucket = 'cowin-details'
    #key = 'area-pin/area-pin-details.txt'
    #obj = s3.Object(bucket, key)
    #pins = eval(obj.get()['Body'].read().decode('utf-8'))
    
    pins = get_area_pins_from_topic()
    #pins = read_env_variable()
    print(pins)
    
    #pin = "209101"
    #pin = '209301'
    #pins = ["208002","208020","209217","208024","208025","209217"]
    
    for pin in pins:
        time.sleep(5)
        date = portal_format
        print('date >> ',date)
        
        final_list = []
        sub_final_dict = {}
        
        url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode="+pin+"&date="+date
        print(url)
        
        try:
            
            res = requests.get(url)
            dict = json.loads(res.text)
            #print(dict)
            #print(dict.keys())
            #print(len(dict['centers']))
            
            for i in dict['centers']:
                #print(i)
                for j in i['sessions']:
                    #print(j.keys())
                    #print(j)
                    if j['available_capacity'] > 0:
                        
                        sub_final_dict['name'] = i['name']
                        sub_final_dict['address'] = i['address']
                        sub_final_dict['district_name'] = i['district_name']
                        sub_final_dict['pincode'] = i['pincode']
                        sub_final_dict['fee_type'] = i['fee_type']
                        sub_final_dict['date'] = j['date']
                        sub_final_dict['min_age_limit'] = j['min_age_limit']
                        sub_final_dict['vaccine'] = j['vaccine']
                        sub_final_dict['available_capacity_dose1'] = j['available_capacity_dose1']
                        sub_final_dict['available_capacity_dose2'] = j['available_capacity_dose2']
                    
                    if sub_final_dict != {}:
                        final_list.append(sub_final_dict)
                    sub_final_dict = {}
            
            if final_list != []:
                temp = ''
                for i in final_list:
                    for k, v in i.items():
                        temp = temp + k + ' : ' + str(v) + '\n'
                    temp = temp + '\n'
                
                #s = '\n'.join(final_list)
                print(temp)
                
                send_sns(temp,pin)
        except Exception as e:
            print(e)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
