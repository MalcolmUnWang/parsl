#include<zmq.hpp>
#include<cstring>
#include<iostream>
#include<fstream>


int main(int argc, char *argv[]){
    std::cout<<"Output";
    int index = 1;
    char * input_function_file;
    char * output_function_file;
    while(index<argc){
        if(std::strcmp(argv[index],"-i") == 0){
            input_function_file = argv[index + 1];
            index += 1;
        }
        else if(std::strcmp(argv[index],"-o") == 0){
            output_function_file = argv[index + 1];
            index += 1;
        }
        else{
            std::cout<<"Command is not supported" << index<<std::endl;
            return 2;
        }
        index++;
    }

    std::cout<<"Output";

    zmq::context_t context(1);

    zmq::socket_t requester(context, ZMQ_REQ);
    requester.connect("tcp://localhost:5556");

    zmq::message_t request(std::strlen(input_function_file));
    memcpy(request.data(), input_function_file, std::strlen(input_function_file));

    requester.send(request);

    zmq::message_t result;
    requester.recv(&result);

    std::fstream outputfile = std::fstream(output_function_file, std::ios::out | std::ios::binary);
    outputfile.write(static_cast<char*>(result.data()),result.size());

    return 0;

}
