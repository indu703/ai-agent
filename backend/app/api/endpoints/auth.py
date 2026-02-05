from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Admin
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    import traceback
    import logging
    import os
    
    # log to file since terminal output is flaky
    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "debug.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"--- LOGIN ATTEMPT: {form_data.username} ---")
        print(f"--- LOGIN ATTEMPT: {form_data.username} ---")
        
        logger.info("Querying database for admin user...")
        admin = db.query(Admin).filter(Admin.username == form_data.username).first()
        
        if not admin:
            logger.warning("RESULT: User not found in database")
            print("RESULT: User not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"User found: {admin.username}. Verifying password...")
        is_valid = verify_password(form_data.password, admin.password_hash)
        logger.info(f"Password verification: {'SUCCESS' if is_valid else 'FAILED'}")
        print(f"Password verification: {'SUCCESS' if is_valid else 'FAILED'}")
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Creating access token...")
        access_token = create_access_token(data={"sub": admin.username})
        logger.info("Login successful, returning token.")
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LOGIN ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"LOGIN ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
