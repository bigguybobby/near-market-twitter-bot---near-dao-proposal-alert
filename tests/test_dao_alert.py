import unittest

from near_dao_alert import Proposal, decode_result, encode_args, format_proposal_tweet, normalize_proposal, proposal_key, unseen


class DaoAlertTests(unittest.TestCase):
    def test_encode_args(self):
        self.assertEqual(encode_args({"id": 7}), "eyJpZCI6IDd9")

    def test_decode_result(self):
        raw = list(b'{"ok": true}')
        self.assertEqual(decode_result({"result": raw}), {"ok": True})

    def test_format_tweet(self):
        proposal = Proposal("council.sputnik-dao.near", 42, "alice.near", "Fund NEAR public goods", "InProgress", "Transfer")
        tweet = format_proposal_tweet(proposal)
        self.assertLessEqual(len(tweet), 280)
        self.assertIn("#42", tweet)
        self.assertIn("alice.near", tweet)

    def test_unseen(self):
        p = Proposal("dao.near", 1, "a.near", "desc")
        self.assertEqual(unseen([p], set()), [p])
        self.assertEqual(unseen([p], {proposal_key(p)}), [])

    def test_normalize_kind_dict(self):
        proposal = normalize_proposal("dao.near", 1, {"proposer": "a.near", "description": "d", "kind": {"Vote": {}}})
        self.assertEqual(proposal.kind, "Vote")


if __name__ == "__main__":
    unittest.main()
