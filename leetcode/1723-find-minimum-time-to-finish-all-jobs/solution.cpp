class Solution {
public:
    bool check(long long mid, vector<int>& j, int i, vector<int> &work, int n){
        if(i == n){
            return true;
        }
        unordered_set<int> mp;
        for(auto &k : work){
            if(mp.count(k)){
                continue;
            }
            if(k + j[i] <= mid){
                k += j[i];
                if(check(mid, j, i+1, work, n)){
                    return true;
                }
                k -= j[i];
                mp.insert(k);
                // if(k == 0){
                //     break;
                // }
            }
        }
        return false;
    }
    int minimumTimeRequired(vector<int>& jobs, int k) {
        int n = jobs.size();
        int l = *max_element(jobs.begin(), jobs.end());
        int r = accumulate(jobs.begin(), jobs.end(), 0);
        int ans = 0; 
        while(r >= l){
            long long mid = (r+l)/2;
            vector<int> work(k, 0);
            if(check(mid, jobs, 0, work, n)){
                ans = mid;
                r = mid-1;
            }else{
                l = mid+1;
            }
        }
        return ans;
    }
};