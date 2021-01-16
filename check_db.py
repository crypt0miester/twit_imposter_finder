from db import session, Me, Imposter

me = session.query(Me).first()
if me: 
    print(me.username, me.image_hash, me.profile_name)
else:
    print("db is empty. run 'python3 main.py' first")
    exit()

query = session.query(Imposter).all()
print("Imposters found: ", len(query))

for imposter in query:
    if imposter.username.lower() != me.username.lower():
        print(imposter.username)
        if imposter.profile_name == me.profile_name:
            print("found a possible match")
            if imposter.image_hash == me.image_hash:
                print("definetly an imposter.")
                print(imposter.username, imposter.profile_name, imposter.image_hash)
                print()