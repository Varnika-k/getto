@echo off
echo ========================================
echo  PUSH FCM PROJECT TO GITHUB
echo ========================================
echo.
echo STEP 1: Make sure you created the GitHub repository first!
echo Repository name: fcm-push-notification-system
echo Visibility: PUBLIC
echo.
echo STEP 2: Replace YOUR_USERNAME below with your GitHub username
echo.
echo STEP 3: Run these commands one by one:
echo.
echo cd C:\Users\VarnikaK\fcm-push-notification-system
echo git remote add origin https://github.com/YOUR_USERNAME/fcm-push-notification-system.git
echo git branch -M main  
echo git push -u origin main
echo.
echo STEP 4: Your repository will be live at:
echo https://github.com/YOUR_USERNAME/fcm-push-notification-system
echo.
echo ========================================
echo  REPOSITORY READY FOR UPLOAD!
echo ========================================
pause