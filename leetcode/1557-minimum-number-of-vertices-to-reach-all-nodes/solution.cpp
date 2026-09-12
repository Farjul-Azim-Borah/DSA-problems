class Solution {
public:
    vector<int> findSmallestSetOfVertices(int n, vector<vector<int>>& edges) {
        vector<int> indegree(n);
        
        for (vector<int> &edge : edges) {
            int u = edge[0], v = edge[1];
            indegree[v]++;
        }

        vector<int> sources;
        for (int i = 0; i < n; i++)
            if (indegree[i] == 0){
                sources.push_back(i);
            }
        
        return sources;
    }
};