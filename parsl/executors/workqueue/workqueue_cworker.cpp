#include<zmq.h>
#include<string.h>
#include<stdio.h>


int main(int argc, char *argv[]){

    printf("Output");
    int index = 1;
    char * input_function_file;
    char * output_function_file;
    while(index<argc){
        if(strcmp(argv[index],"-i") == 0){
            input_function_file = argv[index + 1];
            index += 1;
        }
        else if(strcmp(argv[index],"-o") == 0){
            output_function_file = argv[index + 1];
            index += 1;
        }
        else{
            printf("Command is not supported %d\n",index);
            return 2;
        }
        index++;
    }


    void *context = zmq_ctx_new ();

    void * requester = zmq_socket(context, ZMQ_REQ);
    int rc = zmq_connect(requester, "tcp://localhost:5556");

    zmq_send (requester, input_function_file, strlen(input_function_file), 0);

    char buffer[1000];

    printf("Output");

    zmq_recv (requester, buffer, 1000, 0);

    FILE *fp;
    fp = fopen(output_function_file, "wb");

    fprintf(fp,"%s" ,buffer);

    fclose(fp);
    zmq_close (requester);
    zmq_ctx_destroy (context);
    return 0;

    /*
    zmq::message_t request(std::strlen(input_function_file));
    memcpy(request.data(), input_function_file, std::strlen(input_function_file));

    requester.send(request);

    zmq::message_t result;
    requester.recv(&result);

    std::fstream outputfile = std::fstream(output_function_file, std::ios::out | std::ios::binary);
    outputfile.write(static_cast<char*>(result.data()),result.size());

    return 0;
    */

}
