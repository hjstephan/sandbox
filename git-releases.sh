for repo in ~/Git/*/; do
    if [ -d "$repo/.git" ]; then
        echo -e "\n========================================="
        echo "Repository: $(basename "$repo")"
        echo "========================================="
        
        cd "$repo" || continue
        
        echo "Tags and Releases:"
        git tag --sort=-version:refname | head -10 | while read tag; do
            printf "  %-15s" "$tag"
            
            release_name=$(gh release view "$tag" --json name --jq '.name' 2>/dev/null)
            if [ $? -eq 0 ]; then
                echo "-> Release: $release_name"
            else
                echo "-> (tag only, no release)"
            fi
        done
        
        echo ""
    fi
done
