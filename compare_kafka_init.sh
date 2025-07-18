#!/bin/bash

# Script to compare the two versions of init_kafka_topic.sh

echo "=== Comparing init_kafka_topic.sh versions ==="

if [ -f "init_kafka_topic.sh" ] && [ -f "init_kafka_topic.sh.backup" ]; then
    echo "Both files exist. Running comparison..."
    
    # Show file sizes
    echo -e "\nFile sizes:"
    ls -la init_kafka_topic.sh*
    
    # Show differences
    echo -e "\nDifferences between remote (left) and local backup (right):"
    diff -u init_kafka_topic.sh init_kafka_topic.sh.backup || true
    
    # Check if files are identical
    if cmp -s init_kafka_topic.sh init_kafka_topic.sh.backup; then
        echo -e "\nFiles are identical!"
        echo "You can safely remove the backup: rm init_kafka_topic.sh.backup"
    else
        echo -e "\nFiles are different. Review the differences above."
        echo "The remote version is now active. Your local version is saved as init_kafka_topic.sh.backup"
    fi
else
    echo "Error: One or both files are missing"
    [ ! -f "init_kafka_topic.sh" ] && echo "- init_kafka_topic.sh is missing"
    [ ! -f "init_kafka_topic.sh.backup" ] && echo "- init_kafka_topic.sh.backup is missing"
fi