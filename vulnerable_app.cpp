#include <iostream>
#include <vector>
#include <cstring>

void process_input(const char* input) {
    char buffer[32];
    

    strcpy(buffer, input);

    std::cout << "Input processed without a crash." << std::endl;
}

int main() {
    std::vector<char> input_data;
    char c;
    while (std::cin.get(c)) {
        input_data.push_back(c);
    }

    input_data.push_back('\0');

    process_input(input_data.data());

    return 0; 
}