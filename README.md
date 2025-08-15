# Potauth
Everybody loves potatoes. They are the most fulfilling food you can get, and
they will grow on air. They are rich in a lot of nutrients, and very
energy-dense.

If they're so perfect as foods, why wouldn't they make a good authentication
system, right? That is what this project, originally built for
[Hack Club's Authly](https://authly.hackclub.com), was built to prove how potatoes
can be used as a "great" authentication system. It also proves that I can spend 20
hours of my life in a pointless and foolish joke project and still get paid for it.

Authenticate yourself with a selection of potato-based steps that ensure
your uttermost security at all times, thanks to the best food ever.

# How it works
Potauth is composed of two parts: The web client, and the backend. The backend
handles Most of the logic, though. The web client serves as a simple human-usable
interface for everything on the backend. When you register a new user, the web client
takes your username and favourite type of potato and sends it to the backend server,
alongside your image, encoded in base64. The backend then receives this image,
translates it back into something it can read, and generates a "potato code". The
potato code is in reality just a hash of your image, in such a way that if you have
two identical images, their potato codes will be the exact same. This potato code
becomes your "password," but, unlike traditional passwords, you aren't expected to
remember it. Instead, the backend takes your image and makes a copy of it, taking
out a randomly cropped 256x256 pixel square from the image. This then becomes your
"key." When you log in again, your "key" is sent alongside eight other images, which
are all different from yours. When you select an image, the backend generates its
potato code and checks it against your "key"'s potato code. If they match, you can
log in. Your favourite type of potato is also a way to add more security, since
it makes any person trying to hack into your account need to try seven potato types,
plus nine images. That creates 63 possible combinations for any given username.

Of course, you'll be able to see that this isn't "secure," in the sense that a
bruteforce attack will easily allow any person with your username to log into your
account. However, the purpose of this project is not to be secure or actually be
able to be put to production, but to instead be whim, and fun, and to prove that
potatoes are the best, most nutritional food.

It's just that, a silly demo. Do not judge its security >:(