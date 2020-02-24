#include<iostream>
#include<random>

int main(int argc, char* argv[]) {
    if(argc !=2 ){
        std::cerr << "usage polygon_gen num_rows" <<std::endl;
        return -1;
    }
    char *pEnd;
    int64_t num_rows = std::strtoll(argv[1],&pEnd,10);

    std::random_device rd;
    std::mt19937 mt(rd());
    std::uniform_real_distribution<double> dist(-1,1);

    std::vector<double> points(8);
    std::cout << "num\tpolygon" << std::endl;
    for(int64_t idx=0; idx<num_rows; ++idx){
        for(int i=0;i<(int)points.size();++i) points[i] = dist(mt);
        std::cout << idx << "\tPOLYGON (("
                  << std::fixed
                  << points[0]-2 << " " << points[1]-2 << ","
                  << points[2]-2 << " " << points[3]+2 << ","
                  << points[4]+2 << " " << points[5]+2 << ","
                  << points[6]+2 << " " << points[7]-2 << ","
                  << points[0]-2 << " " << points[1]-2 << "))" << std::endl;
    }
    return 0;
}
