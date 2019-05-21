#include<zmq.h>
#include<string.h>
#include<stdio.h>
#include<stdlib.h>


int main(int argc, char *argv[]){
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
            printf("Command is not supported");
            return 2;
        }
        index++;
    }

    void *context = zmq_ctx_new ();
    void *requester = zmq_socket (context, ZMQ_REQ);
    int rc = zmq_bind (requester, "tcp://localhost:5555");


    char buffer[1000];

    zmq_send(requester, input_function_file, strlen(input_function_file),0);

    zmq_recv(requester, buffer, 1000,0);

    FILE * fp;
    fp = fopen(output_function_file, "wb");
    fputs(buffer,fp);
    fclose(fp);

    return 0;

}