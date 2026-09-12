class Solution {
public:
    vector<int> numOfBurgers(int t, int c) {
        if(t%2 == 1 or t < c){
            return {};
        }
        int v = t/2;
        int l = v-c, r = 2*c-v;
        if(l<0 or r<0){
            return {}; 
        }
        return {v-c, 2*c-v};
    }
};