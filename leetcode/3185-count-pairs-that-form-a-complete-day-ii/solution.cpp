class Solution {
public:
    long long countCompleteDayPairs(vector<int>& hours) {
        long long ans = 0;
        vector<int> hr(24, 0); 
        for(auto i : hours){
            int k = i%24;
            int v = hr[(24-k)%24];
            ans = ans + v;
            hr[k]++;
        }
        return ans;
    }
};