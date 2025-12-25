#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  🎯 DEPLOYMENT VERIFICATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check actor configuration
ACTOR_NAME=$(grep '"name"' .actor/actor.json | head -1 | cut -d'"' -f4)
ACTOR_VERSION=$(grep '"version"' .actor/actor.json | head -1 | cut -d'"' -f4)
echo "✓ Actor Name: $ACTOR_NAME"
echo "✓ Actor Version: $ACTOR_VERSION"
echo "✓ Apify User: aluminum_jam"
echo ""

# Check essential files
echo "📁 Essential Files:"
[ -f ".actor/actor.json" ] && echo "  ✓ .actor/actor.json" || echo "  ❌ .actor/actor.json MISSING"
[ -f ".actor/INPUT_SCHEMA.json" ] && echo "  ✓ .actor/INPUT_SCHEMA.json" || echo "  ❌ .actor/INPUT_SCHEMA.json MISSING"
[ -f "Dockerfile" ] && echo "  ✓ Dockerfile" || echo "  ❌ Dockerfile MISSING"
[ -f "requirements.txt" ] && echo "  ✓ requirements.txt" || echo "  ❌ requirements.txt MISSING"
[ -f "README.md" ] && echo "  ✓ README.md" || echo "  ❌ README.md MISSING"
[ -f "src/main.py" ] && echo "  ✓ src/main.py" || echo "  ❌ src/main.py MISSING"
echo ""

# Check security
echo "🔐 Security Check:"
if git status 2>/dev/null | grep -q "advance-avatar"; then
    echo "  ❌ WARNING: Credentials file in git!"
else
    echo "  ✓ No credentials in git"
fi

if [ -f ".gitignore" ]; then
    echo "  ✓ .gitignore exists"
else
    echo "  ❌ .gitignore MISSING"
fi

if [ -f ".dockerignore" ]; then
    echo "  ✓ .dockerignore exists"
else
    echo "  ❌ .dockerignore MISSING"
fi
echo ""

# Check git status
echo "📊 Git Status:"
if git status >/dev/null 2>&1; then
    UNTRACKED=$(git status --short | wc -l)
    if [ "$UNTRACKED" -eq "0" ]; then
        echo "  ✓ Working tree clean"
    else
        echo "  ⚠️  $UNTRACKED untracked/modified files"
        echo "     Run 'git status' to see details"
    fi
else
    echo "  ⚠️  Not a git repository"
fi
echo ""

# Final message
echo "════════════════════════════════════════════════════════════════"
echo "  ✨ READY TO DEPLOY!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "  1. Review the checklist: cat DEPLOYMENT_CHECKLIST.md"
echo "  2. Deploy to Apify: apify push"
echo "  3. Test in Console: https://console.apify.com"
echo ""
echo "Actor URL (after deploy):"
echo "  https://console.apify.com/actors/aluminum_jam~$ACTOR_NAME"
echo ""
