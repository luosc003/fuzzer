#include <iostream>
#include <vector>
#include <cstdint>
#include <cstdlib>
#include <cstring>

void process_data(const std::vector<char>& data) {
    if (data.size() < 2) {
        return;
    }

    uint16_t length = *reinterpret_cast<const uint16_t*>(data.data());
    
    char* buffer = (char*)malloc(length + 1);

    if (buffer == NULL && (length + 1) > 0) {
        return;
    }
    
    if (data.size() > 2) {
        memcpy(buffer, data.data() + 2, length);
    }
    
    buffer[length] = '\0';

    std::cout << "Data processed: " << buffer << std::endl;
    
    free(buffer);
}

int main() {
    std::vector<char> input_data;
    char c;
    while (std::cin.get(c)) {
        input_data.push_back(c);
    }

    process_data(input_data);

    return 0;
}