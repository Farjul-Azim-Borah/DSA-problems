class Solution {
public:

    void dsu(int n, vector<int> &p){
        for(int i = 0; i<n; ++i){
            p[i] = i;
        }
    }

    int find(int x, vector<int> &p){
        if(p[x] == x){
            return x;
        }
        return p[x] = find(p[x], p);
    }

    void unite(int a, int b, vector<int> &p, int &component){
        a = find(a, p);
        b = find(b, p);
        if(a == b){
            return;
        }
        component--;
        p[b] = a;
    }

    vector<int> solve(int n, int t){
        vector<int> v;
        for(int i = n; i<=t; i += n){
            v.push_back(i);
        }
        return v;
    }
    int countComponents(vector<int>& nums, int t) {
        int n = nums.size();
        vector<int> p(n, 0);
        dsu(n, p);
        map<int, int> mp;
        int ans = n;
        for(int i = 0; i<n; ++i){
            vector<int> v = solve(nums[i], t);
            for(auto j : v){
                if(mp.count(j)){
                    unite(i, mp[j], p, ans);
                }else{
                    mp[j] = i;
                }
            }
        }
        return ans;
    }
};