#!/usr/bin/env bash

# Script to automatically generate documentation from README.md files
# and update the mkdocs.yml navigation structure.

set -e

# Define the mapping from code directories to documentation categories
declare -A DIRECTORY_MAPPING=(
    ["bbbb"]="python"
    ["bbWW"]="bbww"
    ["software"]="software"
    ["src"]="src"
)

# Define the documentation categories and their display names
declare -A DOC_CATEGORIES=(
    ["bbbb"]="HH4b Analysis"
    ["bbWW"]="bbWW Analysis"
    ["software"]="Software"
    ["src"]="Source Code"
)

# Get script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$SCRIPT_DIR"
BASE_PATH="$(dirname "$SCRIPT_DIR")"
MKDOCS_FILE="$DOCS_DIR/mkdocs.yml"

echo "Documentation directory: $DOCS_DIR"
echo "Base repository path: $BASE_PATH"
echo "MkDocs config file: $MKDOCS_FILE"

# Function to generate documentation filename from path
generate_doc_filename() {
    local relative_path="$1"
    
    if [[ "$relative_path" == "README.md" ]]; then
        echo "index.md"
        return
    fi
    
    # Remove README.md from path and convert to filename
    local dir_path=$(dirname "$relative_path")
    if [[ "$dir_path" == "." ]]; then
        echo "index.md"
        return
    fi
    
    # Convert path/to/dir to path-to-dir.md
    echo "${dir_path//\//-}.md"
}

# Function to generate navigation title from path
generate_nav_title() {
    local relative_path="$1"
    
    if [[ "$relative_path" == "README.md" ]]; then
        echo "Overview"
        return
    fi
    
    local dir_path=$(dirname "$relative_path")
    if [[ "$dir_path" == "." ]]; then
        echo "Overview"
        return
    fi
    
    # Convert path/to/dir to "Path To Dir"
    local title=$(echo "$dir_path" | sed 's|/| |g' | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
    echo "$title"
}

# Function to copy README files and generate navigation data
copy_readme_files() {
    local nav_data_file="$DOCS_DIR/.nav_data.tmp"
    > "$nav_data_file"  # Clear the file
    
    for doc_category in "${!DIRECTORY_MAPPING[@]}"; do
        local source_dir="${DIRECTORY_MAPPING[$doc_category]}"
        echo ""
        echo "Processing $doc_category from $source_dir..."
        
        # Create category directory in docs
        local category_docs_dir="$DOCS_DIR/$doc_category"
        mkdir -p "$category_docs_dir"
        
        # Find all README files in the source directory
        local source_path="$BASE_PATH/$source_dir"
        if [[ ! -d "$source_path" ]]; then
            echo "  Warning: Directory $source_path does not exist, skipping..."
            continue
        fi
        
        # Process each README.md file found
        while IFS= read -r -d '' readme_file; do
            # Check if README file is empty
            if [[ ! -s "$readme_file" ]]; then
                echo "  Skipping empty file: $readme_file"
                continue
            fi
            
            # Get relative path from source directory
            local relative_path="${readme_file#$source_path/}"
            
            # Generate target filename
            local target_filename=$(generate_doc_filename "$relative_path")
            local target_path="$category_docs_dir/$target_filename"
            
            # Copy file
            if cp "$readme_file" "$target_path"; then
                echo "  Copied $readme_file -> $target_path"
                
                # Generate navigation info
                local nav_title=$(generate_nav_title "$relative_path")
                local nav_path="$doc_category/$target_filename"
                
                # Store navigation data
                echo "$doc_category|$nav_title|$nav_path" >> "$nav_data_file"
            else
                echo "  Error copying $readme_file"
            fi
        done < <(find "$source_path" -name "README.md" -type f -print0)
    done
}

# Function to update mkdocs.yml navigation
update_mkdocs_nav() {
    local nav_data_file="$DOCS_DIR/.nav_data.tmp"
    
    if [[ ! -f "$nav_data_file" ]]; then
        echo "No navigation data found"
        return
    fi
    
    echo ""
    echo "Updating $MKDOCS_FILE..."
    
    # Create backup
    cp "$MKDOCS_FILE" "$MKDOCS_FILE.backup"
    
    # For each managed category, update only its content while preserving order
    for doc_category in "${!DOC_CATEGORIES[@]}"; do
        local category_name="${DOC_CATEGORIES[$doc_category]}"
        
        # Check if we have files for this category
        if ! grep -q "^$doc_category|" "$nav_data_file" 2>/dev/null; then
            continue
        fi
        
        echo "  Processing category: $category_name"
        
        # Create a temporary file with the new content for this category
        local category_content_file="$DOCS_DIR/.category_content.tmp"
        {
            grep "^$doc_category|" "$nav_data_file" | grep "|Overview|" || true
            grep "^$doc_category|" "$nav_data_file" | grep -v "|Overview|" | sort -t'|' -k2
        } | while IFS='|' read -r category title path; do
            echo "        - $title: $path"
        done > "$category_content_file"
        
        # Use sed to replace the content between the category header and the next top-level item
        # This preserves the order and structure while only updating the managed category content
        local temp_file="$MKDOCS_FILE.tmp"
        local in_target_category=false
        local category_line_pattern="^[[:space:]]*-[[:space:]]*${category_name}:"
        
        while IFS= read -r line; do
            if [[ "$line" =~ $category_line_pattern ]]; then
                # Found our target category
                echo "$line" >> "$temp_file"
                cat "$category_content_file" >> "$temp_file"
                in_target_category=true
            elif [[ "$in_target_category" == true ]]; then
                # Check if this line starts a new top-level category or ends the nav section
                if [[ "$line" =~ ^[[:space:]]{4}-[[:space:]] ]] || [[ "$line" =~ ^[[:alpha:]] ]] || [[ -z "$line" ]]; then
                    # This starts a new section, so we're done with our target category
                    echo "$line" >> "$temp_file"
                    in_target_category=false
                else
                    # Skip this line (it's part of the old category content)
                    continue
                fi
            else
                # Not in our target category, preserve the line
                echo "$line" >> "$temp_file"
            fi
        done < "$MKDOCS_FILE"
        
        # Replace the file with the updated version
        mv "$temp_file" "$MKDOCS_FILE"
        rm -f "$category_content_file"
    done
    
    # Clean up
    rm -f "$nav_data_file"
    
    echo "Updated $MKDOCS_FILE (preserving manual order and structure)"
}

# Function to print summary
print_summary() {
    echo ""
    echo "Documentation generation completed!"
    echo ""
    echo "Summary:"
    
    for doc_category in "${!DOC_CATEGORIES[@]}"; do
        local category_name="${DOC_CATEGORIES[$doc_category]}"
        local category_dir="$DOCS_DIR/$doc_category"
        
        if [[ -d "$category_dir" ]]; then
            local file_count=$(find "$category_dir" -name "*.md" -type f | wc -l)
            echo "  $category_name: $file_count files"
            
            find "$category_dir" -name "*.md" -type f | while read -r file; do
                local filename=$(basename "$file")
                echo "    - $filename"
            done
        fi
    done
}

# Main execution
main() {
    copy_readme_files
    
    if [[ -f "$MKDOCS_FILE" ]]; then
        update_mkdocs_nav
    else
        echo "Warning: $MKDOCS_FILE not found!"
    fi
    
    print_summary
}

# Run main function
main "$@"
