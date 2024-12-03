import time
import json
import os
import numpy as np
from random import sample
import matplotlib.pyplot as plt
import seaborn as sns

# File to store user data
USER_PROFILE_FILE = "user_profiles.json"

# Global variable to track the currently logged-in user
logged_in_user = None


# Helper function to get key press timings (rhythm)
def get_rhythm():
    print("Press keys to create your rhythm. Double press 'Enter' when done.")
    key_timings = []
    previous_time = time.time()

    while True:
        input_key = input("Press a key: ")
        if input_key == '':
            break  # End the rhythm recording on Enter key
        current_time = time.time()
        key_timings.append(current_time - previous_time)
        previous_time = current_time
        print(f"Interval: {current_time - previous_time:.4f} seconds")

    return key_timings


# Load existing user profiles
def load_profiles():
    if os.path.exists(USER_PROFILE_FILE):
        with open(USER_PROFILE_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}


# Save user profiles
def save_profiles(profiles):
    with open(USER_PROFILE_FILE, 'w') as file:
        json.dump(profiles, file, indent = 4)


# Create a new user profile based on rhythm input
def create_profile(profiles):
    username = input("Enter a username to create a profile: ")

    if username in profiles:
        print(f"User '{username}' already exists.")
        return profiles

    rhythm = get_rhythm()

    profiles[username] = {
        'rhythm': rhythm,
        'data': {}
    }

    save_profiles(profiles)
    print(f"Profile for '{username}' created successfully.")
    return profiles


# Compare input rhythm to stored rhythm using mean squared error
def compare_rhythms(input_rhythm, stored_rhythm):
    # Pad shorter rhythms to match lengths
    min_length = min(len(input_rhythm), len(stored_rhythm))
    input_rhythm = input_rhythm[:min_length]
    stored_rhythm = stored_rhythm[:min_length]

    # Calculate mean squared error between the two rhythms
    mse = np.mean((np.array(input_rhythm) - np.array(stored_rhythm)) ** 2)
    return mse


# Perform bootstrapping to calculate the probability of belonging to a user
def bootstrap_rhythm_match(input_rhythm, stored_rhythm, n_resamples=1000, threshold=0.1):
    matches = 0

    # Resample stored rhythm timings and compare
    for _ in range(n_resamples):
        # Randomly resample stored rhythm's timings with replacement
        resampled_rhythm = sample(stored_rhythm, len(input_rhythm))

        # Compare the input rhythm to the resampled rhythm using MSE
        mse = compare_rhythms(input_rhythm, resampled_rhythm)
        if mse < threshold:
            matches += 1

    # Probability is the fraction of resamples that are similar to the input rhythm
    probability = matches / n_resamples
    return probability


# Login to an existing profile
def login(profiles):
    global logged_in_user
    username = input("Enter your username to log in: ")

    if username not in profiles:
        print(f"User '{username}' not found.")
        return None

    print("Please input your rhythm again to verify your identity:")
    input_rhythm = get_rhythm()

    # Perform bootstrapping to get the probability of belonging to the user
    probability = bootstrap_rhythm_match(input_rhythm, profiles[username]['rhythm'])
    print(f"Probability that this rhythm belongs to '{username}': {probability:.4f}")

    # Define a threshold for a valid rhythm match (e.g., 80% probability)
    if probability > 0.8:
        print(f"Login successful for '{username}'!")
        logged_in_user = username  # Set the logged-in user
        return username
    else:
        print(f"Rhythm does not match. Login failed.")
        return None


# Store additional data in the user's profile
def store_data(profiles):
    global logged_in_user
    if logged_in_user:
        data_key = input(f"Enter the data key to store for '{logged_in_user}': ")
        data_value = input(f"Enter the value to store for '{data_key}': ")
        profiles[logged_in_user]['data'][data_key] = data_value
        save_profiles(profiles)
        print(f"Data stored successfully for '{logged_in_user}'.")
    else:
        print("You must be logged in to store data.")


# View data from the user's profile
def view_data(profiles):
    global logged_in_user
    if logged_in_user:
        if profiles[logged_in_user]['data']:
            print(f"Data for '{logged_in_user}':")
            for key, value in profiles[logged_in_user]['data'].items():
                print(f"{key}: {value}")
        else:
            print(f"No data stored for '{logged_in_user}'.")
    else:
        print("You must be logged in to view your data.")


# Visualize the distributions of input and stored rhythms
def visualize_distributions(input_rhythm, stored_rhythm):
    plt.figure(figsize=(12, 6))

    # Plot histogram for input rhythm
    plt.subplot(1, 2, 1)
    sns.histplot(input_rhythm, kde=True, color='blue', bins=10, label='Input Rhythm', stat='density')
    plt.title('Input Rhythm Distribution')
    plt.xlabel('Interval Time (seconds)')
    plt.ylabel('Density')

    # Plot histogram for stored rhythm
    plt.subplot(1, 2, 2)
    sns.histplot(stored_rhythm, kde=True, color='red', bins=10, label='Stored Rhythm', stat='density')
    plt.title('Stored Rhythm Distribution')
    plt.xlabel('Interval Time (seconds)')
    plt.ylabel('Density')

    plt.tight_layout()
    plt.show()


# Logout functionality
def logout():
    global logged_in_user
    if logged_in_user:
        print(f"Logging out user '{logged_in_user}'...")
        logged_in_user = None
        print("Successfully logged out.")
    else:
        print("No user is currently logged in.")


# Main program
def main():
    global logged_in_user
    profiles = load_profiles()

    while True:
        print("\n1. Create new profile")
        print("2. Login to existing profile")
        print("3. Store data in profile")
        print("4. View profile data")
        print("5. Visualize rhythms")
        print("6. Log out")
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            profiles = create_profile(profiles)
        elif choice == '2':
            username = login(profiles)
        elif choice == '3':
            store_data(profiles)
        elif choice == '4':
            view_data(profiles)
        elif choice == '5':
            if logged_in_user:
                input_rhythm = get_rhythm()  # Get a new rhythm for visualization
                stored_rhythm = profiles[logged_in_user]['rhythm']  # Get stored rhythm
                visualize_distributions(input_rhythm, stored_rhythm)
            else:
                print("You must be logged in to visualize rhythms.")
        elif choice == '6':
            logout()
        elif choice == '7':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()


