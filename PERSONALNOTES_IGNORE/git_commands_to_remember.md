check out the most recent commit across all branches globally:

git checkout $(git log --all --pretty=format:%H | Select-Object -First 1)

check out the second most recent commit across all branches globally:

git checkout $(git log --all --pretty=format:%H | Select-Object -First 1)