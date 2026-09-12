class Solution {
public:
    vector<long long> minOperations(vector<int>& nums, vector<int>& q) {
        int n = nums.size();
        vector<long long> pre(n, 0);
        sort(nums.begin(), nums.end());
        pre[0] = nums[0];
        for(int i = 1; i<n; ++i){
            pre[i] = pre[i-1] + nums[i];
        }
        vector<long long> ans;
        for(auto i : q){
            long long idx = upper_bound(nums.begin(), nums.end(), i) - nums.begin();
            idx -= 1;
            if(idx == -1 or idx == n-1){
                ans.push_back(abs(1ll*n*i-pre[n-1]));
            }else{
                long long val1 = (idx+1)*i - pre[idx], val2 = pre[n-1]-pre[idx] - (n-idx-1)*i;
                ans.push_back(val1 + val2);
            }
        }
        return ans; 
    }
};