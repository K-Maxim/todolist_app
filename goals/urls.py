from django.urls import path

from goals import views


urlpatterns = [
    path("board/create", views.BoardCreateView.as_view(), name='create-board'),
    path("board/list", views.BoardListView.as_view(), name='list-board'),
    path("board/<pk>", views.BoardView.as_view(), name='detail-board'),

    path("goal_category/create", views.GoalCategoryCreateView.as_view(), name='create-category'),
    path("goal_category/list", views.GoalCategoryListView.as_view(), name='list-category'),
    path("goal_category/<pk>", views.GoalCategoryView.as_view(), name='detail-category'),

    path("goal/create", views.GoalCreateView.as_view(), name='create-goals'),
    path("goal/list", views.GoalListView.as_view(), name='list-goals'),
    path("goal/<pk>", views.GoalView.as_view(), name='detail-goals'),

    path("goal_comment/create", views.GoalCommentCreateView.as_view(), name='create-comment'),
    path("goal_comment/list", views.GoalCommentListView.as_view(), name='list-comment'),
    path("goal_comment/<pk>", views.GoalCommentView.as_view(), name='detail-comment'),
]
