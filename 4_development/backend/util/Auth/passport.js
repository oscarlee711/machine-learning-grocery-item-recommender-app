const jwtStrategy = require('passport-jwt').Strategy;
const jwtExtract = require('passport-jwt').ExtractJwt;


const options = {
    jwtFromRequest: jwtExtract.fromAuthHeaderAsBearerToken(),
    secretOrKey: process.env.PUBLIC_KEY,
    algorithms: ['RS256']
};

const strategy = new jwtStrategy(options, (payload, done) => {
    try {
        user = payload.sub;
        if (user) {
            return done(null, user);
        } else {
            return done(null, false);
        }
    } catch (error) {
        return done(error, null);
    }
});

module.exports = (passport) => {
    passport.use(strategy);
}