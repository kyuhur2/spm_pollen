@echo on
call conda activate spm_pollen
python main.py --lag_or_ma True --city Fukuoka --num_lags 1
@pause