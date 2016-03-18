# -*- coding: utf-8 -*-
import logging

from puzzle.models.sql import Comment

logger = logging.getLogger(__name__)


class CommentActions(object):
    def comments(self, case_id=None, variant_id=None, username=None):
        """Return comments for a case or variant.

        Args:
            case_id (str): id for a related case
            variant_id (Optional[str]): id for a related variant
        """
        logger.debug("Looking for comments")
        comment_objs = self.query(Comment)

        if case_id:
            comment_objs = comment_objs.filter_by(case_id=case_id)

        if variant_id:
            comment_objs = comment_objs.filter_by(variant_id=variant_id)
        elif case_id:
            comment_objs = comment_objs.filter_by(variant_id=None)

        return comment_objs

    def comment(self, comment_id):
        """Fetch a comment.

        Args:
            comment_id (int): record id from the database
        """
        return self.query(Comment).get(comment_id)

    def add_comment(self, case_obj, text, variant_id=None, username=None):
        """Add a comment to a variant or a case"""

        comment = Comment(
            text=text,
            username=username or 'Anonymous',
            case=case_obj,
            # md5 sum of chrom, pos, ref, alt
            variant_id=variant_id
        )
        self.session.add(comment)
        self.save()
        return comment

    def delete_comment(self, comment_id):
        """Delete a comment"""

        comment_obj = self.query(Comment).get(comment_id)
        if comment_obj:
            logger.debug("Deleting comment {0}".format(comment_obj.id))

        self.session.delete(comment_obj)
        self.save()

        return comment_obj

    def update_synopsis(self, case_obj, text):
        """Update the synopsis for a case."""
        case_obj.synopsis = text
        self.save()
