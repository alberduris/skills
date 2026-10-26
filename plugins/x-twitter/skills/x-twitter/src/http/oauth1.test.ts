import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { oauth1Header, percentEncode } from "./oauth1.ts";

describe("oauth1Header", () => {
  // The worked example on https://docs.x.com/fundamentals/authentication/oauth-1-0a/creating-a-signature,
  // whose published signature is Ls93hJiZbQ3akF3HF3x1Bz8/zU4=. The `status`
  // parameter travels in a form body there; it is signed the same way a query
  // parameter is.
  it("reproduces X's published signature", () => {
    const header = oauth1Header(
      "POST",
      "https://api.x.com/1.1/statuses/update.json",
      {
        include_entities: "true",
        status: "Hello Ladies + Gentlemen, a signed OAuth request!",
      },
      {
        apiKey: "xvz1evFS4wEEPTGEFPHBog",
        apiSecret: "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw",
        accessToken: "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",
        accessTokenSecret: "LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE",
      },
      "kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg",
      "1318622958",
    );

    assert.equal(
      header,
      'OAuth oauth_consumer_key="xvz1evFS4wEEPTGEFPHBog", ' +
        'oauth_nonce="kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg", ' +
        'oauth_signature="Ls93hJiZbQ3akF3HF3x1Bz8%2FzU4%3D", ' +
        'oauth_signature_method="HMAC-SHA1", ' +
        'oauth_timestamp="1318622958", ' +
        'oauth_token="370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb", ' +
        'oauth_version="1.0"',
    );
  });
});

describe("percentEncode", () => {
  it("leaves only RFC 3986 unreserved characters bare", () => {
    assert.equal(percentEncode("AZaz09-._~"), "AZaz09-._~");
    assert.equal(percentEncode("!'()*"), "%21%27%28%29%2A");
    assert.equal(percentEncode(' :"+,/'), "%20%3A%22%2B%2C%2F");
  });

  it("encodes UTF-8 bytes in uppercase hex", () => {
    assert.equal(percentEncode("ñ☃"), "%C3%B1%E2%98%83");
  });
});
