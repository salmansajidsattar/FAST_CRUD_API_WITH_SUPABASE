from fastapi import FastAPI
from models import User
import helper
import bcrypt
import uvicorn
from typing import Union

app=FastAPI()
supabase = helper.create_supabase_client()

def user_exists(key: str = "email", value: str = None):
    global supabase
    user = supabase.from_("users").select("*").eq(key, value).execute()
    print("LOG",(len(user.data) > 0))
    return len(user.data) > 0

@app.get("/")
def application():
    return "Hello World"

@app.post("/user")
def create_user(user: User):
    global supabase
    try:
        # Convert email to lowercase
        user_email = user.email.lower()
        print(user_email)
        # Hash password
        # hased_password = bcrypt.hashpw(str(user.password), bcrypt.gensalt())
        # Check if user already exists
        if user_exists(value=user_email):
            return {"message": "User already exists"}

        # Add user to users table
        user = supabase.from_("users")\
            .insert({"name": user.name, "email": user_email, "password": user.password})\
            .execute()

        # Check if user was added
        if user:
            return {"message": "User created successfully"}
        else:
            print("LOG",user)
            return {"message": "User creation failed"}
    except Exception as e:
        print("Error: ", e)
        return {"message": e}
    
# Retrieve a user
@app.get("/user")
def get_user(user_id: Union[str, None] = None):
    try:
        if user_id:
            user = supabase.from_("users")\
                .select("id", "name", "email")\
                .eq("id", user_id)\
                .execute()

            if user:
                return user
        else:
            users = supabase.from_("users")\
                .select("id", "email", "name")\
                .execute()
            if users:
                return users
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "User not found"}


# Update a user
@app.put("/user")
def update_user(user_id: str, email: str, name: str):
    try:
        user_email = email.lower()

        # Check if user exists
        if user_exists("id", user_id):
            # Check if email already exists
            email_exists = supabase.from_("users")\
                .select("*").eq("email", user_email)\
                .execute()
            if len(email_exists.data) > 0:
                return {"message": "Email already exists"}

            # Update user
            user = supabase.from_("users")\
                .update({"name": name, "email": user_email})\
                .eq("id", user_id).execute()
            if user:
                return {"message": "User updated successfully"}
        else:
            return {"message": "User update failed"}
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "User update failed"}

# Delete a user
@app.delete("/user")
def delete_user(user_id: str):
    try:        
        # Check if user exists
        if user_exists("id", user_id):
            # Delete user
            supabase.from_("users")\
                .delete().eq("id", user_id)\
                .execute()
            return {"message": "User deleted successfully"}

        else:
            return {"message": "User deletion failed"}
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "User deletion failed"}
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
