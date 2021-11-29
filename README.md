# TriviaBot

Hi there! :wave:

TriviaBot server's scope is to facilitate Python knowledge to everyone.


## Here are the features:

### :point_right:    !bot_help

:white_medium_square:Permission roles: everyone

:white_medium_square:Description: Returns all the available commands, their permission roles and descriptions.

### :point_right:    !auth

:white_medium_square:Permission roles: everyone

:white_medium_square:Description: Returns two options:
1. To sign-in and get Player role if you've just joined the server (only Guest).
2. Login - to reactivate Player role (and access all features)
A private channel is created (for admin, bot and user), which is automatically deleted at the end.

### :point_right:    !q

:white_medium_square:Permission roles: Player, PremiumPlayer, PremiumMember, Admin

:white_medium_square:Description: It must be invoke in #trivia-game channel and is available for Players only.
It gives you you questions of two levels of difficulty:
1. Easy - for Player and PremiumPlayer
2. Easy & Hard - for PremiumPlayers
You become a Premium Player after getting 20 points(=20 correct answers).

### :point_right:    !leaderboard

:white_medium_square:Permission roles: Player, PremiumPlayer, PremiumMember, Admin

:white_medium_square:Description: Removes all the #leaderboards channel's messages and display the updated leaderboard.
All the winners get diplomas via email.

### :point_right:    !set_account

:white_medium_square:Permission roles: everyone

:white_medium_square:Description: It sets a game account with the amount of 0.0 lei.
If the account exists already, displays the sold.

### :point_right:    !manage_account

:white_medium_square:Permission roles: everyone

:white_medium_square:Description: If the account doesn't exist, ask you to set one. Otherwise, creates a private channel for admin, bot and author. Then, the user has 6 options:
1. Check his account balance
2. Buy Premium Member Title (100lei)
3. Refund his account
4. Donate to TriviaBot server
5. Generate account statement via email
6. Exit & Delete channel

### :point_right:    !server_report

:white_medium_square:Permission roles: PremiumMember, Admin

:white_medium_square:Description: Creates a new private channel & generates TriviaBot server's financial report: total sold and revenues from PremiumMember Titles, Donations and Ads, and theirs corresponding transactions numbers. At the end, the channel is deleted.

### :point_right:    !myself

:white_medium_square:Permission roles: PremiumMember

:white_medium_square:Description: Creates a new private channel & generates a report about user's activity on TriviaBot Server: info about membership, game and account. At the end, the channel is deleted.

### :point_right:    !friend_donation @user.mention int_amount

:white_medium_square:Permission roles: PremiumMember

:white_medium_square:Description: If the sold allows, the donation is done. If the friend doesn't have an account yet, one is being set up before the donation.

### :point_right:    !weather City

:white_medium_square:Permission roles: PremiumMember

:white_medium_square:Description: Gives the weather info for the desired city, if found. The output is displayed in #support-premium-members-only channel.

### :point_right:    !review

:white_medium_square:Permission roles: everyone

:white_medium_square:Description: Allows author to review the server.
If he has already given a review, it shows him the last feedback and ask if an update is desired. If yes, server saves the new review.
Otherwise, a first review is saved.
The updated server's rating score is displayed at the end. The score only considers the last feedback of each member (if many).

### :point_right:    !rating

:white_medium_square:Permission roles: everyone

:white_medium_square:Description: Gives Trivia Bot updated rating score. The score only considers the last feedback of each member (if many).

### :point_right:    !role @user.mention Role

:white_medium_square:Permission roles: Admin

:white_medium_square:Description: Gives/Removes a user's specific role if doesn't/does have it.

### :point_right:    !clear

:white_medium_square:Permission roles: everyone

:white_medium_square:Description: Removes all the channel's messages!


### :point_right:    NOTES:

:white_medium_square:Guest role: Is automatically assigned when the user joins the TriviaBot server.

:white_medium_square:Ads: Are displayed in #general channel at random times: 2, 3, 4 or 5 min.


##### Legend: everyone = Guest, Player, PremiumPlayer, PremiumMember, Admin

## Thank you!
