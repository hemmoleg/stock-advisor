docker DB: docker-compose up
backend: python run.py
frotend: cd frontend -> npm run start

access DB: - docker exec -it stock_advisor_db bash
           - psql -U user -d stock_advisor
           - select * from prediction_summary
           - <SQL code>

- change route name /make_prediction to /make_prediction_today

- add new route /make_prediction_for_date
  - get news for some companies for date a month ago (opening course)
  - then check prediction (next day closing course)

- add redux to frontend

- newsapi
- newscatcher

---> figure out how to properly get closing_price for stock on date
     (WITHOUT the timeinterval thing) -> get_closing_price_at_date
     THEN commit!