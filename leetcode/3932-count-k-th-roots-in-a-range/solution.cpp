class Solution {
public:

    int countKthRoots(int l, int r, int k) {
        int count = 0;
        int k1 = 1;
        if(k == 1){
            return (r-l+1);
        }
        while(true){
            long long v = 1;
            for(int i = 1; i<=k; ++i){
                v = v*k1;
                if(v > r){
                    break;
                }
            }
            if(v >= l && v <= r){
                count++; 
            }
            if(v > r){
                break;
            }
            k1++; 
        }
        if(l == 0){
            count = count+1;
        }
        return count; 
    }
};