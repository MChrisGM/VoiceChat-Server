from VoiceChat import VoiceClient, get_io, filter_io

if __name__=='__main__':

    ip = '192.168.56.1'
    port = 8080

    print('Starting client')

    filtered_io = filter_io(get_io(), ['index','name'])
    # print(json.dumps(filtered_io, indent=4))
    for i in filtered_io['Input']:
        print(filtered_io['Input'][i]['index'],filtered_io['Input'][i]['name'])
    input_id = int(input('Select Input Device ID: '))
    
    for i in filtered_io['Output']:
        print(filtered_io['Output'][i]['index'],filtered_io['Output'][i]['name'])
    output_id = int(input('Select Output Device ID: '))

    client = VoiceClient(ip = ip, port=port, input_device_id=input_id, output_device_id=output_id)
    client.start_stream()
    client.start_receive()