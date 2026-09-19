class Solution {
public:
    vector<int> resultsArray(vector<vector<int>>& q, int k) {
        vector<int> ans;
        priority_queue<long long> pq;
        for(auto i : q){
            int a = i[0], b = i[1];
            long long dist = abs(a) + abs(b);
            pq.push(dist);
            if(pq.size() > k){
                pq.pop();
                ans.push_back(pq.top());
            }else if(pq.size() < k){
                ans.push_back(-1);
            }else{
                ans.push_back(pq.top());
            }
        }
        return ans;
    }
};