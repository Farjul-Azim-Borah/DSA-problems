class Solution {
public:
    bool check(vector<pair<long long, long long>> &vp, long long mid){
        int n = vp.size();
        long long val = vp[0].first;
        for(int i = 1; i<n; ++i){
            val = max(vp[i].first, val + mid);
            if(val > vp[i].second){
                return false;
            }
        }
        return true; 
    }
    int maxPossibleScore(vector<int>& start, int d) {
        vector<pair<long long, long long>> vp;
        for(auto i : start)    {
            vp.push_back({i, i+d});
        }
        sort(vp.begin(), vp.end());
        long long ans = 0; 
        long long l = 1, r = 1e18;
        while(r >= l){
            long long mid = (r+l)/2;
            if(check(vp, mid)){
                ans = mid;
                l = mid+1;
            }else{
                r = mid-1; 
            }
        }
        return ans; 
    }
};