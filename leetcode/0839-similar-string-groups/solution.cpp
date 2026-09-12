class Solution {
public:
    bool check(string s, string t){
        int n = s.size();
        int count = 0;
        string st = "", st1 = "";
        for(int i = 0; i<n; ++i){
            if(s[i] != t[i]){
                count++; 
                st += s[i];
                st1 += t[i];
            }
            if(count > 2){
                return false;
            }
        }
        sort(st.begin(), st.end());
        sort(st1.begin(), st1.end());
        return st == st1;
    }
    vector<int> vis;
    vector<string> str;
    int n;  
    void dfs(string s){
        for(int i = 0; i<n; ++i){
            if(s == str[i]){
                vis[i] = 1; 
                continue;
            }
            if(vis[i] == 1){
                continue;
            }
            if(check(s, str[i])){
                vis[i] = 1;
                dfs(str[i]);
            }
        }
    }
    int numSimilarGroups(vector<string>& strs) {
        n = strs.size();
        int ans = 0;
        vis.assign(n, 0);
        str = strs; 
        for(int i = 0; i<n; ++i){
            if(vis[i] == 0){
                dfs(str[i]);
                ans++;
            }
        }
        return ans;
    }
};