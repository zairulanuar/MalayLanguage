#!/bin/bash
# Cloud Run Configuration Verification Script

echo "==== Cloud Run Configuration Consistency Check ===="

echo ""
echo "1. CHECKING PORT CONFIGURATION:"
echo "   Dockerfile PORT setting:"
grep "ENV PORT" Dockerfile
echo "   app.yaml PORT setting:"
grep "PORT:" app.yaml
echo "   cloudbuild.yaml PORT setting:"
grep "'--port'" cloudbuild.yaml

echo ""
echo "2. CHECKING MALAYA_CACHE CONFIGURATION:"
echo "   Dockerfile MALAYA_CACHE:"
grep "ENV MALAYA_CACHE" Dockerfile
echo "   app.yaml MALAYA_CACHE:"
grep "MALAYA_CACHE:" app.yaml
echo "   cloudbuild.yaml MALAYA_CACHE:"
grep "MALAYA_CACHE=" cloudbuild.yaml

echo ""
echo "3. CHECKING HOST CONFIGURATION:"
echo "   app.yaml HOST:"
grep "HOST:" app.yaml
echo "   cloudbuild.yaml HOST:"
grep "HOST=" cloudbuild.yaml

echo ""
echo "==== VERIFICATION COMPLETE ===="
echo ""
echo "Expected Results:"
echo "✓ All PORT values should be 8080"
echo "✓ All MALAYA_CACHE values should be /tmp/.malaya"
echo "✓ All HOST values should be 0.0.0.0"
